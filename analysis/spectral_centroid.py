import numpy as np
import librosa

def spectral_centroid(D, fft_freqs, 
                      prevent_blow_up=False, zero_below_percent=.05):
    D = np.abs(D) # Strip complex part and take magnitudes
    mag_sums = np.sum(D,0)
    peak_mag = mag_sums.max()
    scs = []
    for t in range(np.shape(D)[1]):
        D_at_t = D[:, t]
        spectral_sum = np.sum(D_at_t)
        if spectral_sum < 1.0 and prevent_blow_up:
            spectral_sum = 1.0
        if mag_sums[t] < peak_mag * zero_below_percent:
            scs.append(0.0)
        else:
            scs.append(np.sum(fft_freqs * D_at_t) / spectral_sum)
    return scs
    
def spectral_metrics_for_file(path, n_fft=2048):
    y, sr = librosa.load(path, sr=16000)
    D = librosa.stft(y, n_fft=n_fft)
    fft_freqs = librosa.fft_frequencies(16000, n_fft)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    scs = spectral_centroid(D, fft_freqs)
    mean_sc = np.mean(scs)
    return(mean_sc, onset_env)
    
def scs_for_file(path, n_fft=2048):
    y, sr = librosa.load(path, sr=16000)
    D = librosa.stft(y, n_fft=n_fft)
    fft_freqs = librosa.fft_frequencies(16000, n_fft)
    scs = spectral_centroid(D, fft_freqs)
    return(scs)

def mean_sc_for_file(path, n_fft=2048):
    scs = scs_for_file(path, n_fft)
    mean_sc = np.mean(scs)
    return(mean_sc)
    
