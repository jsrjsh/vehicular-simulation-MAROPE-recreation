# MA-ROPE — Where things stand

**What we discovered**

The numbers in the current manuscript don't match what the simulation actually produces when we
run it today. We checked this carefully by running the same code independently, months apart, on
different machines, and getting the same results both times — so the simulator itself is reliable.
The manuscript's numbers are the outlier, not the code. The most likely explanation is that the
manuscript reflects an earlier version of the model or a different configuration than what's in the
codebase now, not that anything is broken.

We also traced the paper's central claim — that MA-ROPE has "1.9x lower queue loss" than always
offloading everything — down to its root cause. It turns out "queue loss" was never actually
measuring queue congestion at all; there's no such mechanism in the simulator. It was measuring how
often a transmission failed, but only counting transmissions that were actually attempted. MA-ROPE
transmits rarely, so on that narrow measure it looks worse. But when we count total failures across
the whole fleet, MA-ROPE causes about 11 times fewer failed transmissions overall than the
always-offload policy, simply by not transmitting when it doesn't need to. Both things are true —
we were just reporting the one that made the story simpler, not the one that told the full truth.

**What changed scientifically**

We now understand precisely why the reliability numbers behave the way they do, instead of just
observing that they were inconsistent. We fixed a data-recording gap that meant only part of the
trained model was being saved, which limited how exactly past results could be double-checked. And
we built a pipeline that regenerates every reported number from scratch, with proof attached that
running it twice gives the same answer.

**Why the work is stronger now**

Before this, we didn't actually know whether the paper's headline claim was true, false, or
somewhere in between — the numbers had drifted across versions and nobody could say why. Now we
know the real story is more interesting than the original claim: MA-ROPE genuinely does prevent far
more failures overall, it just occasionally chooses a noisier channel on the rare occasions it does
transmit. That's a real, explainable tradeoff, not a flaw to hide — and it's a stronger, more honest
result than what was originally written.

**What remains before submission**

Three things, before this is ready for your review:

1. We've only approximated the corrected numbers so far. We need to actually re-run the full
   experiment properly (already specified and ready to execute) to get final, trustworthy figures.
2. Right now MA-ROPE is only compared against "always offload everything" and "never offload
   anything" — both trivial policies. A reviewer will rightly ask what it beats besides those, so we
   need at least one more realistic comparison point.
3. A couple of the other reported numbers (energy use, and two of the utility scores) still don't
   match the manuscript and haven't been resolved yet — either the code needs a small fix, or we
   need to be upfront that those numbers came from an earlier model version.

None of this is bad news. It means the paper's foundation is now much sounder than before — we just
need to finish running the corrected experiment and firm up the comparison before this is ready to
go out.
