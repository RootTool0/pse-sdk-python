import pse
import random

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
button.location = (200, 200, -100)
button.create()

# door = pse.Door()
# door.location = (-150, 0, -100)
# door.create()

cube = pse.WeightCube()
cube.location = (200, -200, 0)
cube.create()

@button.on_element_changed()
def Test(state):
    if state != 0:
        button.location = (random.randint(-500, 500), random.randint(-500, 500), -100)

while True:
    pse.poll_events()
