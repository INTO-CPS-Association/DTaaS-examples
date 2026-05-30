import { useEffect, useMemo, useRef, useState } from 'react'
import { io } from 'socket.io-client'
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import bitsLogo from '../assets/BITS_Pilani-Logo.png'
import intoCpsLogo from '../assets/into-cps-logo.png'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || `http://${window.location.hostname}:4000`
const WINDOW_SECONDS = 120
const SAMPLE_INTERVAL_MS = 1000

export default function App() {
  const socketRef = useRef(null)
  const pointCounterRef = useRef(0)
  const latestPowerRef = useRef(0)

  const [connectionStatus, setConnectionStatus] = useState('connecting')
  const [currentPower, setCurrentPower] = useState(0)
  const [powerHistory, setPowerHistory] = useState([])
  const [mode, setMode] = useState('forward')
  const [pan, setPan] = useState(90)
  const [tilt, setTilt] = useState(45)
  const [targetPowerInput, setTargetPowerInput] = useState('10')
  const [requestedTargetPower, setRequestedTargetPower] = useState(10)
  const [optimizedPan, setOptimizedPan] = useState(null)
  const [optimizedTilt, setOptimizedTilt] = useState(null)
  const [isTargetUnachievable, setIsTargetUnachievable] = useState(false)
  const [estimatedMinPower, setEstimatedMinPower] = useState(null)
  const [estimatedMaxPower, setEstimatedMaxPower] = useState(null)
  const [clampedState, setClampedState] = useState('none')
  const [optimizerState, setOptimizerState] = useState('idle')

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ['polling'] })
    socketRef.current = socket

    socket.on('connect', () => {
      setConnectionStatus('connected')
    })

    socket.on('disconnect', () => {
      setConnectionStatus('disconnected')
    })

    socket.on('control_mode', (payload) => {
      if (!payload || typeof payload !== 'object') {
        return
      }

      const nextMode = payload.mode === 'inverse' ? 'inverse' : 'forward'
      setMode(nextMode)
    })

    socket.on('telemetry_update', (payload) => {
      if (!payload || typeof payload.current_power !== 'number') {
        return
      }

      const nextPower = Number(payload.current_power.toFixed(2))
      latestPowerRef.current = nextPower
      setCurrentPower(nextPower)
    })

    const handleOptimizationUpdate = (payload) => {
      if (!payload || typeof payload !== 'object') {
        return
      }

      const nextPan =
        typeof payload.target_pan === 'number'
          ? payload.target_pan
          : typeof payload.pan === 'number'
            ? payload.pan
            : null
      const nextTilt =
        typeof payload.target_tilt === 'number'
          ? payload.target_tilt
          : typeof payload.tilt === 'number'
            ? payload.tilt
            : null

      if (nextPan !== null) {
        setOptimizedPan(Number(nextPan.toFixed(2)))
      }
      if (nextTilt !== null) {
        setOptimizedTilt(Number(nextTilt.toFixed(2)))
      }

      if (typeof payload.estimated_min_power === 'number') {
        setEstimatedMinPower(Number(payload.estimated_min_power.toFixed(2)))
      }

      if (typeof payload.estimated_max_power === 'number') {
        setEstimatedMaxPower(Number(payload.estimated_max_power.toFixed(2)))
      }

      if (typeof payload.clamped === 'string') {
        setClampedState(payload.clamped)
      }

      if (typeof payload.state === 'string') {
        setOptimizerState(payload.state)
      }

      const unachievable =
        payload.unachievable === true ||
        payload.achievable === false ||
        payload.clamped === 'min' ||
        payload.clamped === 'max' ||
        payload.status === 'unachievable'
      setIsTargetUnachievable(unachievable)
    }

    socket.on('model_update', handleOptimizationUpdate)
    socket.on('optimization_result', handleOptimizationUpdate)

    return () => {
      socket.off('model_update', handleOptimizationUpdate)
      socket.off('optimization_result', handleOptimizationUpdate)
      socket.off('control_mode')
      socket.off('connect')
      socket.off('disconnect')
      socket.disconnect()
      socketRef.current = null
    }
  }, [])

  useEffect(() => {
    const timer = window.setInterval(() => {
      pointCounterRef.current += 1
      const nextPoint = {
        step: pointCounterRef.current,
        power: latestPowerRef.current,
      }

      setPowerHistory((prev) => [...prev, nextPoint].slice(-WINDOW_SECONDS))
    }, SAMPLE_INTERVAL_MS)

    return () => {
      window.clearInterval(timer)
    }
  }, [])

  useEffect(() => {
    if (!socketRef.current) {
      return
    }

    socketRef.current.emit('control_mode', { mode })
  }, [mode])

  const handleTargetPowerChange = (event) => {
    const nextValue = event.target.value
    setTargetPowerInput(nextValue)
  }

  const handleApplyAngles = () => {
    if (!socketRef.current || mode !== 'forward') {
      return
    }

    socketRef.current.emit('set_angles', { pan, tilt })
  }

  const handleRunOptimization = () => {
    if (!socketRef.current || mode !== 'inverse') {
      return
    }

    const parsed = Number(targetPowerInput)
    if (!Number.isFinite(parsed) || parsed < 0) {
      return
    }

    setRequestedTargetPower(parsed)
    socketRef.current.emit('control_mode', { mode: 'inverse' })
    socketRef.current.emit('update_target_power', { target: parsed })
  }

  const modeLabel = useMemo(
    () => (mode === 'forward' ? 'Forward Mode (Manual)' : 'Inverse Mode (AI Optimization)'),
    [mode]
  )

  const connectionLabel = useMemo(() => {
    if (connectionStatus === 'connected') {
      return 'Connected'
    }

    if (connectionStatus === 'disconnected') {
      return 'Disconnected'
    }

    return 'Connecting'
  }, [connectionStatus])

  const chartData = useMemo(() => {
    const lastIndex = powerHistory.length - 1
    return powerHistory.map((point, index) => ({
      x: index - lastIndex,
      power: point.power,
    }))
  }, [powerHistory])

  const chartUpperBound = useMemo(() => {
    const candidates = [25, requestedTargetPower + 5]

    if (typeof estimatedMaxPower === 'number') {
      candidates.push(estimatedMaxPower + 4)
    }

    if (chartData.length > 0) {
      candidates.push(Math.max(...chartData.map((point) => point.power)) + 3)
    }

    return Math.max(...candidates)
  }, [chartData, estimatedMaxPower, requestedTargetPower])

  const formatRelativeTime = (secondsOffset) => {
    if (!Number.isFinite(secondsOffset)) {
      return 'now'
    }

    const secondsAgo = Math.max(0, Math.round(Math.abs(secondsOffset)))
    return secondsAgo === 0 ? 'now' : `-${secondsAgo}s`
  }

  const targetSummary = useMemo(() => {
    if (mode === 'forward') {
      return 'Manual pose control'
    }

    if (isTargetUnachievable) {
      return 'Target clamped to reachable limit'
    }

    return 'Tracking requested target'
  }, [isTargetUnachievable, mode])

  return (
    <main className="min-h-dvh text-slate-900">
      <div className="relative isolate overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.22),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(14,165,233,0.16),_transparent_28%),linear-gradient(180deg,_#f8fbff_0%,_#eef5fb_46%,_#ffffff_100%)]" />
        <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[linear-gradient(180deg,_rgba(15,23,42,0.05),_transparent)]" />

        <div className="relative mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 lg:px-8 lg:py-6">
          <header className="rounded-[2rem] border border-white/80 bg-white/80 px-5 py-5 shadow-[0_24px_80px_rgba(15,23,42,0.10)] backdrop-blur-md sm:px-6">
            <div className="grid items-center gap-4 lg:grid-cols-[auto,1fr,auto] lg:gap-6">
              <img
                src={bitsLogo}
                alt="BITS Pilani logo"
                className="h-14 w-auto object-contain sm:h-16 lg:h-18"
                loading="eager"
              />

              <div className="text-center">
                <p className="text-[1.4rem] font-semibold uppercase tracking-[0.2em] text-black">
                  Solar Panel Digital Twin Research Interface
                </p>
                {/* <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">
                  Telemetry, Optimization, and Experimental Control
                </h2> */}
                
              </div>

              <img
                src={intoCpsLogo}
                alt="INTO-CPS logo"
                className="h-14 w-auto justify-self-end object-contain sm:h-16 lg:h-18"
                loading="eager"
              />
            </div>

            {/* <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4">
              <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
                <StatusPill tone={connectionStatus === 'connected' ? 'green' : connectionStatus === 'disconnected' ? 'red' : 'slate'}>
                  {connectionLabel}
                </StatusPill>
                <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">{modeLabel}</span>
              </div>
              <p className="text-sm font-medium text-slate-500">{targetSummary}</p>
            </div> */}
          </header>

          {/* <section className="mt-6 grid gap-4 md:grid-cols-3"> */}
          <section className="mt-6 flex flex-row justify-center">
            <MetricCard
              label="Live Power"
              value={`${currentPower.toFixed(2)} W`}
              note="Current telemetry from the gateway"
              accent="sky"
            />
            {mode === 'inverse' ? (
              <>
                {/* <MetricCard
                  label="Estimated Operating Window"
                  value={`${formatPowerValue(estimatedMinPower)} - ${formatPowerValue(estimatedMaxPower)}`}
                  note={`Clamp behavior: ${clampedState}`}
                  accent="emerald"
                /> */}
                <MetricCard
                  label="Optimized Pose"
                  value={`${optimizedPan ?? '--'}° / ${optimizedTilt ?? '--'}°`}
                  note={`Solver state: ${optimizerState}`}
                  accent="violet"
                />
              </>
            ) : null}
          </section>

          <section className="mt-6 grid gap-6 lg:grid-cols-[380px,1fr]">
            <aside className="rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-[0_24px_70px_rgba(15,23,42,0.08)] backdrop-blur-md sm:p-6">
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.35em] text-sky-700/80">Control Surface</p>
                  <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">Operating Mode</h2>
                </div>
                <StatusPill tone={mode === 'inverse' ? 'violet' : 'sky'}>{mode === 'forward' ? 'Manual' : 'AI'}</StatusPill>
              </div>

              <div className="grid grid-cols-2 rounded-2xl bg-slate-100 p-1">
                <ModeButton active={mode === 'forward'} onClick={() => setMode('forward')}>
                  Forward
                </ModeButton>
                <ModeButton active={mode === 'inverse'} onClick={() => setMode('inverse')}>
                  Inverse
                </ModeButton>
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Forward mode sends manual angle commands. Inverse mode asks the optimizer to infer the best pose for the
                requested power target.
              </p>

              {mode === 'forward' ? (
                <div className="mt-6 space-y-5">
                  <RangeControl
                    label="Pan"
                    min={0}
                    max={180}
                    step={1}
                    value={pan}
                    onChange={setPan}
                    unit="°"
                  />
                  <RangeControl
                    label="Tilt"
                    min={0}
                    max={90}
                    step={1}
                    value={tilt}
                    onChange={setTilt}
                    unit="°"
                  />
                  <button
                    type="button"
                    onClick={handleApplyAngles}
                    className="h-12 w-full rounded-2xl bg-slate-950 px-4 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2"
                  >
                    Apply Angles
                  </button>
                </div>
              ) : (
                <div className="mt-6 space-y-5">
                  <label className="block">
                    <div className="mb-2 flex items-center justify-between text-sm font-medium text-slate-700">
                      <span>Target Power</span>
                      <span className="font-mono text-sky-700">{requestedTargetPower.toFixed(1)} W</span>
                    </div>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      inputMode="decimal"
                      value={targetPowerInput}
                      onChange={handleTargetPowerChange}
                      className="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-base text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
                      placeholder="Enter target power (W)"
                    />
                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      The optimizer will clamp beyond-range requests to the nearest reachable limit.
                    </p>
                  </label>

                  <button
                    type="button"
                    onClick={handleRunOptimization}
                    className="h-12 w-full rounded-2xl bg-sky-600 px-4 text-sm font-semibold text-white transition hover:bg-sky-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2"
                  >
                    Run Optimization
                  </button>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Optimized Orientation</p>
                    <div className="mt-4 grid gap-3 text-sm text-slate-700">
                      <InfoRow label="Target Pan" value={`${optimizedPan ?? '--'}°`} />
                      <InfoRow label="Target Tilt" value={`${optimizedTilt ?? '--'}°`} />
                    </div>
                    {isTargetUnachievable ? (
                      <p className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                        Requested power is outside the reachable envelope. The system is showing the closest safe approximation.
                      </p>
                    ) : null}
                  </div>
                </div>
              )}
            </aside>

            <section className="rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-[0_24px_70px_rgba(15,23,42,0.08)] backdrop-blur-md sm:p-6">
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 pb-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.35em] text-sky-700/80">Telemetry View</p>
                  <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">Power History</h2>
                </div>
                <div className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
                  Window: {WINDOW_SECONDS}s
                </div>
              </div>

              <div className="mt-5 h-[360px] w-full sm:h-[440px]">
                <ResponsiveContainer>
                  <LineChart data={chartData} margin={{ top: 10, right: 24, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="4 4" stroke="#dbe5ef" />
                    <XAxis
                      dataKey="x"
                      type="number"
                      domain={[-WINDOW_SECONDS + 1, 0]}
                      ticks={[-120, -90, -60, -30, 0]}
                      stroke="#64748b"
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      tickFormatter={formatRelativeTime}
                    />
                    <YAxis
                      domain={[0, Math.ceil(chartUpperBound / 5) * 5]}
                      stroke="#64748b"
                      tick={{ fill: '#64748b', fontSize: 12 }}
                    />
                    <Tooltip
                      labelFormatter={formatRelativeTime}
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        border: '1px solid #dbe5ef',
                        borderRadius: 16,
                        color: '#0f172a',
                        boxShadow: '0 20px 50px rgba(15, 23, 42, 0.08)',
                      }}
                    />
                    {mode === 'inverse' && Number.isFinite(requestedTargetPower) ? (
                      <ReferenceLine
                        y={requestedTargetPower}
                        stroke="#0f766e"
                        strokeDasharray="6 6"
                        label={{ value: 'Target', position: 'right', fill: '#0f766e', fontSize: 12 }}
                      />
                    ) : null}
                    <Line
                      type="monotone"
                      dataKey="power"
                      stroke="#0284c7"
                      strokeWidth={3}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className={`mt-4 grid gap-3 border-t border-slate-200 pt-4 ${mode === 'inverse' ? 'sm:grid-cols-2 xl:grid-cols-4' : 'sm:grid-cols-2'}`}>
                <InfoCard label="Mode" value={mode === 'forward' ? 'Manual' : 'AI Optimization'} />
                <InfoCard label="Connection" value={connectionLabel} />
                {mode === 'inverse' ? <InfoCard label="Target" value={`${requestedTargetPower.toFixed(1)} W`} /> : null}
                {mode === 'inverse' ? <InfoCard label="Solver" value={optimizerState} /> : null}
              </div>
            </section>
          </section>
        </div>
      </div>
    </main>
  )
}

function RangeControl({ label, min, max, step, value, onChange, unit }) {
  return (
    <label className="block">
      <div className="mb-2 flex items-center justify-between text-sm font-medium text-slate-700">
        <span>{label}</span>
        <span className="font-mono text-sky-700">
          {value}
          {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-sky-500"
      />
    </label>
  )
}

function ModeButton({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`h-11 rounded-xl px-4 text-sm font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2 ${
        active
          ? 'bg-white text-slate-950 shadow-sm'
          : 'text-slate-600 hover:bg-white/70 hover:text-slate-900'
      }`}
    >
      {children}
    </button>
  )
}

function MetricCard({ label, value, note, accent }) {
  const accentMap = {
    sky: 'from-sky-500/15 to-cyan-500/5 text-sky-700',
    emerald: 'from-emerald-500/15 to-teal-500/5 text-emerald-700',
    violet: 'from-violet-500/15 to-fuchsia-500/5 text-violet-700',
  }

  return (
    <div className={`rounded-[1.5rem] border border-white/80 bg-gradient-to-br p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)] ${accentMap[accent] || accentMap.sky}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">{label}</p>
      <p className="mt-4 font-mono text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">{value}</p>
      <p className="mt-3 text-sm leading-6 text-slate-600">{note}</p>
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl bg-white px-3 py-2">
      <span className="text-slate-500">{label}</span>
      <span className="font-mono font-semibold text-slate-900">{value}</span>
    </div>
  )
}

function InfoCard({ label, value }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">{label}</p>
      <p className="mt-2 text-sm font-medium text-slate-900">{value}</p>
    </div>
  )
}

function StatusPill({ tone, children }) {
  const toneMap = {
    green: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    red: 'border-rose-200 bg-rose-50 text-rose-700',
    violet: 'border-violet-200 bg-violet-50 text-violet-700',
    sky: 'border-sky-200 bg-sky-50 text-sky-700',
    slate: 'border-slate-200 bg-slate-50 text-slate-700',
  }

  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] ${toneMap[tone] || toneMap.slate}`}>
      {children}
    </span>
  )
}

function formatPowerValue(value) {
  if (!Number.isFinite(value)) {
    return '-- W'
  }

  return `${value.toFixed(2)} W`
}
