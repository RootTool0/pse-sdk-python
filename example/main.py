import pse

# Connect to the running game
pse.initialize()

# Build a floor
pse.StaticMesh.create(
    location=(0, 0, -100),
    scale=(10, 10, 1),
    mesh=pse.Mesh.FACE,
    material=pse.Material.FLOOR_WHITE,
)

# Create a button and a door
button = pse.Button()
button.create(location=(200, 200, -100))

door = pse.Door()
door.create(location=(-150, 0, -100))

# Open the door when the button is pressed
@button.on_element_changed()
def on_button_changed(state):
    door.state = state

# Main loop
while True:
    pse.poll_events()
