# @title Enhanced Lossless vs False Lossless Analysis

import subprocess
import sys
import logging
import shutil
import numpy as np
import soundfile as sf
import os
from tempfile import NamedTemporaryFile
from concurrent.futures import ThreadPoolExecutor

# ---- Configuration ----
TARGET_SAMPLE_RATE = 44100
THRESHOLD_PERCENTAGE = 0.01
CUTOFF_FREQ_THRESHOLD = 20000
SPECTROGRAM_RESOLUTION = "1920x1080"
audio_file = ""  # @param {type:"string"}


# ---- Setup Logging ----
def setup_logging():
    """Configure professional logging with improved formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Create colored formatter
    formatter = logging.Formatter("%(levelname)s:%(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logging()


def check_and_install_ffmpeg():
    """Check and install FFmpeg with better error handling"""
    if not shutil.which("ffmpeg"):
        logger.info("FFmpeg not found. Installing...")
        try:
            subprocess.run(
                ["apt-get", "update"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["apt-get", "install", "-y", "ffmpeg"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("FFmpeg installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg installation failed: {e}")
            sys.exit(1)


def run_ffmpeg_command(cmd):
    """Execute FFmpeg command with timeout and better error handling"""
    logger.debug(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=True,
        )
        logger.debug(result.stdout)
        return True
    except subprocess.TimeoutExpired:
        logger.error("Command timed out after 5 minutes")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False


def generate_spectrogram(input_path, output_path):
    """Generate spectrogram with parallel processing"""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        input_path,
        "-lavfi",
        f"showspectrumpic=s={SPECTROGRAM_RESOLUTION}",
        output_path,
    ]
    return run_ffmpeg_command(cmd)


def convert_to_mono_wav(input_path, output_path):
    """Convert audio to mono WAV with optimized parameters"""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        str(TARGET_SAMPLE_RATE),
        "-c:a",
        "pcm_s16le",  # Specify PCM 16-bit
        "-fflags",
        "+bitexact",  # Ensure consistent output
        output_path,
    ]
    return run_ffmpeg_command(cmd)


def analyze_spectrum(wav_path):
    """Analyze audio spectrum with optimized FFT calculation"""
    try:
        data, samplerate = sf.read(wav_path, always_2d=True)
        data = data.mean(axis=1)  # Convert to mono if not already

        # Use optimized FFT with Hamming window
        window = np.hamming(len(data))
        fft = np.fft.rfft(data * window)
        freqs = np.fft.rfftfreq(len(data), d=1 / samplerate)
        magnitude = np.abs(fft)

        # Normalize magnitude
        magnitude = magnitude / np.max(magnitude)

        # Find cutoff frequency
        threshold = THRESHOLD_PERCENTAGE
        valid_indices = np.where(magnitude > threshold)[0]

        if len(valid_indices) == 0:
            logger.warning("No significant frequencies detected")
            return 0

        cutoff_freq = freqs[valid_indices[-1]]

        # Calculate energy distribution
        energy_below_20k = np.sum(magnitude[freqs <= CUTOFF_FREQ_THRESHOLD])
        total_energy = np.sum(magnitude)
        ratio = energy_below_20k / total_energy

        return {
            "cutoff_freq": cutoff_freq,
            "energy_ratio": ratio,
            "freqs": freqs,
            "magnitude": magnitude,
        }
    except Exception as e:
        logger.error(f"Spectrum analysis failed: {e}")
        return None


def analyze_audio(file_path):
    """Main analysis function with optimized workflow"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Analyzing: {file_path}")

    # Generate spectrogram in parallel with conversion
    with ThreadPoolExecutor() as executor:
        spectrogram_future = executor.submit(
            generate_spectrogram, file_path, "/content/spectrogram.png"
        )

        # Use temporary file for conversion
        with NamedTemporaryFile(suffix=".wav") as temp_wav:
            if not convert_to_mono_wav(file_path, temp_wav.name):
                logger.error("Audio conversion failed")
                return

            spectrum_data = analyze_spectrum(temp_wav.name)

    # Wait for spectrogram to complete
    spectrogram_future.result()
    logger.info("Spectrogram generated: /content/spectrogram.png")

    if not spectrum_data:
        logger.error("Analysis failed")
        return

    # Enhanced verdict with more metrics
    cutoff = spectrum_data["cutoff_freq"]
    ratio = spectrum_data["energy_ratio"]

    logger.info(f"Cutoff frequency: {cutoff:.2f} Hz")
    logger.info(f"Energy below 20kHz: {ratio:.2%}")

    if cutoff < CUTOFF_FREQ_THRESHOLD * 0.95:  # 5% margin
        logger.info("Verdict: STRONG INDICATION OF LOSSY ORIGIN")
        logger.info("- Frequency content drops significantly before 20kHz")
        if ratio > 0.99:
            logger.info("- Over 99% of energy is concentrated below 20kHz")
    else:
        logger.info("Verdict: LIKELY GENUINE LOSSLESS")
        logger.info("- Significant frequency content up to 20kHz")
        if ratio < 0.95:
            logger.info("- Noticeable energy above 20kHz detected")


# ---- Main Execution ----
if __name__ == "__main__":
    check_and_install_ffmpeg()

    if audio_file.strip():
        analyze_audio(audio_file)
    else:
        logger.error("No audio file specified")
