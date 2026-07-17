Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: 3-day +80/−60 bracket-replay, realized option PnL; N=1,375 fills (full-window n=806)
Source: docs/DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md; INTELLIGENCE_BRIEF 2026-06-02 (H16)
Date: 2026-07-17

# V/OI > 2 does NOT improve selection — anti-edge, gate relaxed

The first honest realized-option-PnL backtest (H16) showed the `V/OI > 2` conviction gate
**removes ~55–63% of real option winners** while its precision lift is statistically ≤ 0
(full-window n=806, real +25%: lift −0.031, bootstrap 90% CI **[−0.061, −0.001]**,
P(lift≤0)=95.7%; stable across chronological halves). This SUPERSEDED the 2026-05-06
lit-audit "heuristic but works, hold at 2.0" stance — on realized PnL it does not even work
as conviction.

Correction to an earlier leaked-label audit: that pass used `peak_return_3d` (an UNDERLYING
peak, 78.5% base win rate) and mis-fingered `OI ≥ 10` as the worst gate; on realized OPTION
PnL, OI ≥ 10 flips to neutral/positive because it is a fillability gate and the filled
cohort is conditioned on fillability ([[oi-not-quality-signal]]). Do NOT relax OI/vol; DO
relax V/OI. Gate removed globally 2026-06-02 (owner-directed, trivial revert).
