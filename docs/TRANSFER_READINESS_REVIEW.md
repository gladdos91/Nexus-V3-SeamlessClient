# V1 transfer readiness proposal

## Purpose and provenance

This is a source proposal for Casimir to review and integrate. Base source is
SE-Nexus/SeamlessClient commit `8b2cfd605f0af743d6dfb1cb1394f5a789d5b44a`.
See UPSTREAM.md and LICENSE.txt. This repository is independent, so use its PR diff
or cherry-pick the patch commit when integrating; GitHub cannot open a normal
cross-repository PR unless the repositories share a fork network.

The supplied 3.1.12.0 DLL contains a different coordinator/sector implementation.
This proposal targets the public baseline's default V1 path (`UseNewVersion = false`),
not a recovered copy of that DLL. Experimental V2 remains unchanged. Assembly
version and wire protocol remain upstream values; this is not a packaged release.

## Confirmed startup issue

The later loader/game logs establish a private-accessor MethodAccessException
in the uploaded 3.1.12.0 build, plus a cleanup NullReferenceException. See
[3112_STARTUP_FAILURE.md](3112_STARTUP_FAILURE.md) for the source correction
and exact-build metadata repair. That concrete error must be fixed before
attributing transfer symptoms to timing.

## Evidence and limits

Binary inspection found join completion occurring before replication/player
readiness. The supplied game log showed full reloads, duplicate TorchServerMod,
and missing-faction relation errors, but no Seamless transfer diagnostics. Those
observations do not establish that this change fixes the reported incident.
No player logs, DLLs, account identifiers, or server configuration are committed.

## Behavior

- Keep a V1 transfer active until the destination acknowledges its replication
  batch, a live local character/identity/controller exists, and control is bound.
- Subscribe before requesting the batch; capture its exact client and ignore stale
  callbacks and duplicate/old-client join notifications.
- Recover control of an unparented character when ownership is missing or points
  to a closed entity. Preserve existing cockpit/remote control and do not call
  SpawnIntoCharacter, Stand, or force an exit from a parent.
- Restore the entity camera, reset on-foot input, and rebuild HUD controls once.
- Replace the five-minute background watchdog/repeated seamless reconnect with a
  single 90-second deadline evaluated on the update thread. On failure, release
  plugin state, unpause, log the phase, and tell the player to disconnect/rejoin.
  This deliberately does not automatically reconnect, respawn, or recreate grids.
- Remove batch/host/P2P handlers on completion, cancellation, failure, and disposal.
- Guard bare `/nexus` against an argument-index exception.

`PendingReplicablesDone` acknowledges the requested batch, not every grid anywhere
in the world. Normal distance-based streaming continues after completion. Dead,
spectating, or deliberately characterless clients can hit the deadline and need
an ordinary reconnect; a maintainer may choose to support those modes separately.
The 90-second limit needs testing under heavy worlds and slow connections.
Mod lifecycle notifications retain their existing upstream timing.

## Validation status

Completed here: C# syntax parsing, project compile-item coverage, patch whitespace
check, and manual review of subscription/request ordering and terminal cleanup.

Not completed: compilation against Space Engineers 1.210.014, Harmony patch binding,
or a live Nexus transfer. This environment has no .NET build toolchain or game
reference DLLs. Do not deploy this branch as a tested replacement binary.

## Required maintainer checks before release

1. Run SetupSolution.bat against the target client's Bin64, restore packages, and
   build SeamlessClient.sln in Release using VS/.NET Framework 4.8 tooling.
2. Confirm the Harmony `OnUserJoined` postfix binds `__instance` and JoinResultMsg.
3. Transfer on foot with player arrival before batch completion and in the reverse
   order. Neither ordering should finish until both conditions are ready.
4. Cross a sector in a cockpit and while remotely controlling a grid. Verify camera
   and ownership remain correct and the character is not forcibly ejected.
5. Delay character creation: transfer remains pending and recovers when it arrives.
   Verify a closed controlled entity can be replaced with the live on-foot character.
6. Reject a join, drop destination P2P, disconnect, and exceed the deadline. Expect
   one failure message, no reconnect loop, no lingering overlay, and no pause.
7. Attempt overlapping transfers, then complete/fail and begin a second transfer.
   Deliver an old-client join/batch event; it must not complete the new transfer.
8. Repeat at least ten sector crossings; check handlers do not accumulate and verify
   missing grids, input, camera, faction data, and mod state independently.
9. Test bare `/nexus`, normal `/nexus refreshcharacter`, and plugin disposal while a
   transfer is waiting. Validate the experimental V2 path separately if enabled.
