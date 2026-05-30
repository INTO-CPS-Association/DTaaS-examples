function SliderRow({ label, value, min, max, step, unit, onChange }) {
  return (
    <label className="block space-y-2">
      <div className="flex items-center justify-between text-sm font-medium text-slate-800">
        <span>{label}</span>
        <span className="font-mono text-cyan-900">
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
        className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-emerald-600"
      />
    </label>
  )
}

export default function Controls({ mode, setMode, pan, setPan, tilt, setTilt, targetPower, setTargetPower }) {
  return (
    <div className="rounded-3xl border border-cyan-900/10 bg-white/80 p-5 shadow-panel backdrop-blur-sm">
      <h2 className="text-lg font-semibold text-slate-900">Control Surface</h2>
      <p className="mt-1 text-sm text-slate-600">Switch between manual panel control and target-power optimization.</p>

      <div className="mt-5 grid grid-cols-2 gap-2 rounded-2xl bg-slate-100 p-2">
        <button
          type="button"
          onClick={() => setMode('forward')}
          className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
            mode === 'forward'
              ? 'bg-cyan-800 text-white shadow'
              : 'bg-transparent text-slate-700 hover:bg-slate-200'
          }`}
        >
          Forward
        </button>
        <button
          type="button"
          onClick={() => setMode('inverse')}
          className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
            mode === 'inverse'
              ? 'bg-emerald-700 text-white shadow'
              : 'bg-transparent text-slate-700 hover:bg-slate-200'
          }`}
        >
          Inverse
        </button>
      </div>

      <div className="mt-5 space-y-5">
        {mode === 'forward' ? (
          <>
            <SliderRow label="Pan Angle" value={pan} min={0} max={180} step={1} unit="°" onChange={setPan} />
            <SliderRow label="Tilt Angle" value={tilt} min={0} max={90} step={1} unit="°" onChange={setTilt} />
          </>
        ) : (
          <SliderRow
            label="Target Power"
            value={targetPower}
            min={0}
            max={20}
            step={0.1}
            unit="W"
            onChange={setTargetPower}
          />
        )}
      </div>
    </div>
  )
}
