# SeamlessClientPlugin (Re-write)

## How it works
With Nexus servers, all data is shared between servers. (Factions, Identities, Players, Econ etc) This is a huge benefit as we dont have to go in and reload all identities and factions etc. The next thing that happens is that the server tells the client to switch to the proper server. It then goes in and just re-applies the MyMultiplayerClient to the target server. Of course there is a few other things that must happen to fix any errors or bugs, but that is the main rundown.



## How to install
Simply install the plugin loader, and check this plugin's box to be added to the plugin loaders' active plugin list. (SE will need to be restarted afterwards)


## Known issues
Obviously this is not an issue-free system. Currently, since im doing no mod unloading or loading, there could be issues if your servers don't have the same mods, or the mods don't work right. Please do not swarm mod authors with faults if seamless doesn't play nice with it. ***Its not their fault*** its ***mine***. I will be trying to implement mod unloading and loading switching between servers, just no ETA.

## ModAPI
I attempted to avoid implementing any modAPI in seamless, but unfortunately, Space Engineers doesn't handle unloading and reloading the same mod without compiling easily. Either I compile the mod every time you switch servers, eventually running into memory issues, or I attempt to unload the mod manually and restart it.
In both scenarios, unloading static variables are often up to the mod author and sometimes are set to null. On mod load, these variables are not re-instantiated with the default values resulting in many issues. It is way easier for mod authors when needed implement seamless unload and load logic appropriately.

There are two methods you can add to your mods (In the main mod session component class)

private void SeamlessServerLoaded(){}
private void SeamlessServerUnloaded(){}

Unloaded happens when seamless starts switching, Loaded when seamless is done switching. Seamless patches these methods on mod compilation.


