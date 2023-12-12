package dtmanager;

public class Clock {
	private java.time.Clock internalClock = java.time.Clock.systemUTC();
	private int now = 0;
	
	public void increaseTime(int amount) {
		this.now += amount;
	}
	
	public int getNow() {
		return this.now;
	}
	
	public void setClock(int value) {
		this.now = value;
	}
}
