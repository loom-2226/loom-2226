CLOSED = "E1_INTERFACE_CLOSED"
HELD = "E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD"
BLOCKED = "OPEN_BLOCKING_E1"
COMPONENT = "OPEN_BLOCKING_COMPONENT_CERTIFICATION_ONLY"

HOLDS = (
    "SOURCE_REACTOR_REALIZABILITY",
    "DIRECTED_ENERGY_REMASS_COUPLING_PARTITION",
    "RADIATION_AND_PARTICLE_DEPOSITION",
    "WORKING_FLUID_STORAGE_FEED_IMPLEMENTATION",
    "MAGNETIC_NOZZLE_PHYSICS_AND_LIFETIME",
    "SHIELD_MAGNET_THERMAL_LIFETIME",
    "THRUST_FRAME_DYNAMICS_LOCAL_LOAD_AND_FATIGUE",
    "PHYSICAL_PLUME_EXTERNAL_HARDWARE_CLEARANCE",
    "RCS_INTEGRATION",
)


def build_review():
    classes = {
        "primary_torch_vehicle_contract": CLOSED,
        "source_energy_thermal_dependency_chain": HELD,
        "remass_feed_nozzle_requirement_interface": HELD,
        "structural_plume_operational_requirement_interface": HELD,
    }

    blockers = []

    return {
        "schema": "LOOM.Wayfarer.E1TorchIntegratedQualificationReview",
        "status": HELD if not blockers else BLOCKED,
        "e1_interface_frozen": not blockers,
        "component_hardware_certified": False,
        "earned_interfaces": ("T1", "T2", "T3", "T4"),
        "classifications": classes,
        "open_blocking_e1": blockers,
        "component_certification_holds": HOLDS,
        "counts": {
            CLOSED: sum(v == CLOSED for v in classes.values()),
            HELD: sum(v == HELD for v in classes.values()),
            BLOCKED: len(blockers),
            COMPONENT: len(HOLDS),
        },
        "authority": {
            "e1_torch_vehicle_interface": not blockers,
            "reactor_source_certified": False,
            "working_fluid_selected": False,
            "feed_hardware_certified": False,
            "magnetic_nozzle_certified": False,
            "physical_plume_certified": False,
            "thrust_frame_certified": False,
            "radiator_hardware_certified": False,
            "rcs_installation_certified": False,
        },
    }
