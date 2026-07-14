import pse

pse.initialize()

for x in range(5):
    for y in range(5):
        # plane = pse.DynamicMesh()
        # plane.location = (x * 200 - 400, y * 200 - 400, -100)
        # plane.mesh = pse.Mesh.FACE
        # plane.material = pse.Material.FLOOR_WHITE if (x + y) % 2 == 0 else pse.Material.FLOOR_BLACK
        # plane.create()
        pse.StaticMesh.create(
            location=(x * 200 - 400, y * 200 - 400, -100),
            mesh=pse.Mesh.FACE,
            material=pse.Material.FLOOR_WHITE if (x + y) % 2 == 0 else pse.Material.FLOOR_BLACK
        )

button = pse.Button()
button.location = (0, 0, -100)
button.create()

door = pse.Door()
door.location = (-150, 0, -100)
door.create()

cube = pse.WeightCube()
cube.location = (0, 0, 200)
cube.create()

@button.on_element_changed()
def Test(state):
    if state != 0: return
    global cube

    if cube:
        cube.destroy()

    cube = pse.WeightCube()
    cube.location = (0, 0, 200)
    cube.create()

while True:
    pse.poll_events()
