# Figure 4 placeholder: CRLB_features versus CRLB_waveform

CAPTION. Per-parameter Cramer-Rao lower bound from the feature channel (amplitude
0.05 mV, timing 5 ms) versus from the waveform channel (white Gaussian 0.025 mV
per sample per lead), restricted to the 8 independent leads I, II, V1 to V6, since
III, aVR, aVL, aVF are exact linear combinations of I and II and a 12-lead diagonal
noise model would over-count the Fisher information by roughly 12/8. A CRLB-to-CRLB
comparison (never CRLB to contraction); the per-parameter gap is the Fisher
information lost by summarizing the waveform into features (I_S <= I_X, equality iff
sufficient). At REFERENCE_THETA the feature CRLB is looser than the 8-lead waveform
CRLB for every parameter, by a factor of about 21 (init_length_lv) to about 70 (cv)
(delta_IV about 32, init_length_rv about 48, branch_angle about 33, w about 43,
cv_myo about 64), so the 15-feature summary discards most of the waveform's
per-parameter Fisher information under these stated floors. Restricting to 8 leads
raises the waveform CRLB only slightly (a few percent), so the gap is a feature-vs-
waveform effect, not a lead-redundancy artifact. Numbers from
outputs/crlb_comparison.json; code supplies the real figure.
