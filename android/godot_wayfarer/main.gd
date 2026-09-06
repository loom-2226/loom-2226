extends Node3D

var model_root: Node3D
var camera: Camera3D
var status_label: Label
var yaw := 0.55
var pitch := 0.45
var distance := 85.0
var target := Vector3(28.0, 0.0, 0.0)
var drag_active := false
var last_touch := Vector2.ZERO

func _ready() -> void:
    _build_environment()
    _load_wayfarer()
    _update_camera()

func _build_environment() -> void:
    model_root = Node3D.new()
    model_root.name = "WayfarerModel"
    add_child(model_root)

    camera = Camera3D.new()
    camera.name = "Camera"
    camera.current = true
    camera.fov = 42.0
    add_child(camera)

    var key := DirectionalLight3D.new()
    key.name = "KeyLight"
    key.rotation_degrees = Vector3(-35.0, -35.0, 0.0)
    key.light_energy = 2.2
    add_child(key)

    var fill := DirectionalLight3D.new()
    fill.name = "FillLight"
    fill.rotation_degrees = Vector3(25.0, 145.0, 0.0)
    fill.light_energy = 0.65
    add_child(fill)

    var ui := CanvasLayer.new()
    ui.name = "HUD"
    add_child(ui)

    status_label = Label.new()
    status_label.name = "Status"
    status_label.position = Vector2(18.0, 18.0)
    status_label.text = "LOOM WAYFARER — GODOT ANDROID GLB TEST"
    ui.add_child(status_label)

func _load_wayfarer() -> void:
    var path := "res://wayfarer.glb"
    if status_label == null:
        push_error("Wayfarer HUD status label was not initialized")
        return
    if not ResourceLoader.exists(path):
        status_label.text += "\nMissing wayfarer.glb — generate it from LOOM geometry JSON first."
        return
    var resource := ResourceLoader.load(path)
    var packed := resource as PackedScene
    if packed == null:
        status_label.text += "\nGLB import failed: resource is not a PackedScene."
        push_error("wayfarer.glb did not import as PackedScene")
        return
    var instance := packed.instantiate()
    if instance == null:
        status_label.text += "\nGLB instantiate failed."
        push_error("wayfarer.glb PackedScene instantiate returned null")
        return
    model_root.add_child(instance)
    status_label.text += "\nGLB loaded. Drag to orbit. Pinch/wheel to zoom."

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        drag_active = event.pressed
        last_touch = event.position
    elif event is InputEventScreenDrag:
        yaw -= event.relative.x * 0.008
        pitch = clamp(pitch + event.relative.y * 0.008, -1.35, 1.35)
        _update_camera()
    elif event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_LEFT:
            drag_active = event.pressed
            last_touch = event.position
        elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
            distance = max(18.0, distance - 4.0)
            _update_camera()
        elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
            distance = min(180.0, distance + 4.0)
            _update_camera()
    elif event is InputEventMouseMotion and drag_active:
        yaw -= event.relative.x * 0.008
        pitch = clamp(pitch + event.relative.y * 0.008, -1.35, 1.35)
        _update_camera()
    elif event is InputEventMagnifyGesture:
        distance = clamp(distance / max(event.factor, 0.1), 18.0, 180.0)
        _update_camera()

func _update_camera() -> void:
    if camera == null:
        return
    var cp := cos(pitch)
    var pos := Vector3(
        target.x + distance * cp * cos(yaw),
        target.y + distance * sin(pitch),
        target.z + distance * cp * sin(yaw)
    )
    camera.position = pos
    camera.look_at(target, Vector3.UP)
