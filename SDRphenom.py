import numpy as np
from rtlsdr import RtlSdr
import time

def calculate_coherence(samples):
    """
    Measures the non-randomness of a signal.
    1.0 = Pure White Noise (Random)
    Lower values = Higher structure/coherence.
    """
    # Calculate Power Spectral Density
    psd = np.abs(np.fft.fft(samples))**2
    psd /= np.sum(psd) # Normalize
    
    # Calculate Spectral Entropy
    entropy = -np.sum(psd * np.log2(psd + 1e-12))
    max_entropy = np.log2(len(psd))
    
    # Normalize entropy to a 0.0 - 1.0 scale
    return entropy / max_entropy

def main():
    from rtlsdr import RtlSdrTcpClient
sdr = RtlSdrTcpClient(hostname='127.0.0.1', port=1234)
    
    # Target natural/uncommon bands (e.g., 142 MHz range or VLF if using Direct Sampling)
    # Note: 1420.4 MHz is the Hydrogen Line (Cosmic Baseline)
    freqs_to_scan = np.linspace(142e6, 145e6, 10) 
    
    sdr.sample_rate = 2.048e6
    sdr.gain = 'auto'

    print(f"{'Freq (MHz)':<12} | {'Coherence Score':<18} | {'Status'}")
    print("-" * 50)

    try:
        while True:
            for freq in freqs_to_scan:
                sdr.center_freq = freq
                time.sleep(0.1) # Let the frequency settle
                
                samples = sdr.read_samples(1024*16)
                score = calculate_coherence(samples)
                
                # We define "Intelligence" as anything with a score significantly lower 
                # than the average noise floor (usually around 0.85-0.95 for SDRs)
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
