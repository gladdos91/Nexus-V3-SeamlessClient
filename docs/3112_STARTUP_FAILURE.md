# Confirmed 3.1.12.0 startup failure

The October 25 loader log reports:

```text
System.MethodAccessException: Attempt by method 'SeamlessClient.Seamless.Update()'
to access method 'SeamlessClient.Components.SectorTransferEngine.get_isSeamlessSwitching()' failed.
```

The game log confirms the sector component patched, then startup update failed.
Cleanup subsequently throws NullReferenceException in SectorTransferEngine.Destroy.
This occurs at startup, before transfer testing, and is separate from the earlier
hypothesis about incomplete player/entity readiness.

## Source fix for the maintainer's 3.1.12 branch

That branch is not in the public source imported here. Its inspected DLL declares
both `isSeamlessSwitching` accessors private. Give the getter assembly visibility
while retaining the private setter:

```csharp
internal static bool isSeamlessSwitching { get; private set; } = false;
```

Use that member only from the same assembly. A normal source rebuild should catch
other illegal private-member accesses; avoid rewriting IL that emits such calls.
Make `Destroy()` tolerate partial initialization (`myCommands?.Dispose()`), and
clean subscriptions/state even when initialization did not finish. The V1 patch
in this PR includes the corresponding null-safe command cleanup.

## Reproducible repair of the exact supplied binary

`tools/repair_3112_access.py` accepts only the inspected DLL's SHA256 and changes
only the getter's MethodDef member-access bits from Private to Assembly. It needs
Python 3 and no packages, does not execute the DLL, and refuses to overwrite files.
Example from the repository root, with the game closed:

```powershell
py -3 tools/repair_3112_access.py "C:\path\to\SeamlessClient.dll" "C:\path\to\SeamlessClient-access-repair.dll"
```

Back up the original, replace only the loader's active local SeamlessClient.dll
with the repaired file under that original name, and keep just one enabled copy.
Loader-managed downloads may replace local changes. The repair does not address
the partial-initialization cleanup bug or apply the source V1 readiness changes.

Verified statically against the attachment: assembly/version unchanged, exactly
one byte changed, getter is now assembly-visible, setter remains private. No game
code or dependencies changed. This has not been run inside Space Engineers.
Re-test startup first; if startup succeeds, capture a fresh transfer log. Do not
assume this resolves missing grids, characters, controls, or faction data.
