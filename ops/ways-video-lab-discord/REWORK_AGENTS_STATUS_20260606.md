# WAYS rework agents status

Time: 2026-06-06T09:13:07Z

Josh asked if we are reworking the failed candidates and whether to spin up agents. Agents were spun up in two waves:

1. Strict rework-packet agents for Saturn, Octopus, Tardigrade.
2. Source-acquisition agents for Saturn, Octopus, Tardigrade.

No new videos were rendered. No public upload/publish happened. Old failed MP4s remain audit-only.

## Saturn Hexagon Storm

- Packet: `test_cases/saturn_hexagon_storm/SATURN_HEXAGON_STORM_STRICT_WAYS_REWORK_PACKET.md`
- Source manifest: `test_cases/saturn_hexagon_storm/assets/source_nasa/source_manifest.json`
- Source status: `test_cases/saturn_hexagon_storm/outputs/gate2_plate_qc/SOURCE_ACQUISITION_STATUS.md`
- State: source acquisition started; NASA/JPL/Cassini candidates acquired.
- Blocker: Shot 03 still needs clean non-text Earth scale proxy and proof plates/contact sheet.

## Octopus Three Hearts

- Packet: `test_cases/octopus_three_hearts/OCTOPUS_THREE_HEARTS_WAYS_REWORK_PACKET.md`
- Source manifest: `test_cases/octopus_three_hearts/assets/source_rework/source_manifest.json`
- Source status: `test_cases/octopus_three_hearts/outputs/gate2_plate_qc/SOURCE_ACQUISITION_STATUS.md`
- State: 5 local real octopus candidates acquired plus one URL-only lead.
- Blocker: rights/attribution recheck and contact-sheet visual QC needed; no accepted text-free anatomy proof diagram yet.

## Tardigrade Survival Mode

- Packet: `test_cases/tardigrade_survival_mode/STRICT_WAYS_REWORK_PACKET.md`
- Source manifest: `test_cases/tardigrade_survival_mode/assets/source_rework/source_manifest.json`
- Source status: `test_cases/tardigrade_survival_mode/outputs/gate2_plate_qc/SOURCE_ACQUISITION_STATUS.md`
- State: open-source microscope/research candidates shortlisted.
- Blocker: Wikimedia 429 blocked downloads; water-return/reactivation beat still not gate-ready.

## Current policy

These are **source/plate rework lanes only**. Do not render again until Gate 2 source/plate QC passes. Do not surface generated videos until template, voice, plates, and per-shot say-dog-see-dog all pass.
