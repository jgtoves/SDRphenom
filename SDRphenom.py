import numpy as np
import time
# Removed 'from rtlsdr import RtlSdr' to avoid library errors in Termux

def calculate_coherence(samples):
    psd = np.abs(np.fft.fft(samples))**2
    psd /= np.sum(psd)
    entropy = -np.sum(psd * np.log2(psd + 1e-12))
    max_entropy = np.log2(len(psd))
    return entropy / max_entropy

def main():
    # Only import the TCP client
    from rtlsdr import RtlSdrTcpClient
    
    try:
        # Connect to the Android RTL-SDR Driver App (ensure it's running!)
        sdr = RtlSdrTcpClient(hostname='127.0.0.1', port=1234)
    except Exception as e:
        print(f"Connection Failed: {e}")
        print("Tip: Ensure the 'RTL-SDR Driver' app is running its TCP server on port 1234.")
        return

    freqs_to_scan = np.linspace(142e6, 145e6, 10) 
    sdr.sample_rate = 2.048e6
    sdr.gain = 'auto'

    print(f"{'Freq (MHz)':<12} | {'Coherence Score':<18} | {'Status'}")
    print("-" * 50)

    try:
        while True:
            for freq in freqs_to_scan:
                sdr.center_freq = freq
                # Increased sleep slightly for TCP stability
                time.sleep(0.2) 
                
                # Flush the buffer to get 'fresh' data for the new frequency
                _ = sdr.read_samples(1024) 
                
                samples = sdr.read_samples(1024*16)
                score = calculate_coherence(samples)
                
                status = "QUIET"
                if score < 0.75: status = "STRUCTURED"
                if score < 0.60: status = "HIGH COHERENCE - INVESTIGATE"
                
                print(f"{freq/1e6:<12.3f} | {score:<18.4f} | {status}")
            
            print("\n--- Scan Cycle Complete ---\n")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping Scan...")
    finally:
        sdr.close()

if __name__ == "__main__":
    main()
