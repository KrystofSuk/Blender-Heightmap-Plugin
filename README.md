# Blender Heightmap Plugin

Small plugin which I've created to help me with repetetive tasks of importing large terrains into Blender and Unreal from World Creator. 

## How to

1. You'll need to obtain heightmap of desired terrain to displace. I reccomend having more bit depth than 8, otherwise it could get jaggy.
2. You can find the Heightmap tab on right in View mode.
3. Set the size of the terrain in x,y,z.
4. Specify to how many tiles should be on one side = if you'll say 4 tiles, the plane willbe divided into 4*4 tiles.
5. Next modify the displacement smoothing amount, which affects how many polygons there will be. The pre displacement subdivision subdivides the mesh before displacement is applied. The post displacement is applied after displacement and smoothes out the finsihed mesh.
6. Set heightmap path.
7. You can either go one by one (Create tiles > Add Modifiers > Apply Modifiers > Recenter Pivots) or do all the steps at once (Do All).
8. The process is heavily dependent on the hardware and the number of subdivisions and resulting number of polygons, it can take even half an hour with 135 milion of polygons.

