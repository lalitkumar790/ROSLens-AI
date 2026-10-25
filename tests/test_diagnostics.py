from app.diagnostics import diagnose_log


def ids(log: str) -> set[str]:
    return {item["id"] for item in diagnose_log(log)["diagnostics"]}


def test_package_missing():
    result = diagnose_log("Package 'my_robot_pkg' not found")
    assert result["diagnostics"][0]["id"] == "package-not-found"
    assert "not found" in result["diagnostics"][0]["evidence"][0]


def test_tf_extrapolation():
    assert "tf-extrapolation" in ids("Lookup would require extrapolation into the future")


def test_qos_mismatch():
    assert "qos-incompatible" in ids("New publisher discovered on topic with incompatible QoS")


def test_multiple_candidates_are_reported():
    found = ids("Package 'robot_bringup' not found\nSegmentation fault")
    assert {"package-not-found", "node-crash"} <= found


def test_unknown_error_falls_back():
    result = diagnose_log("Some novel subsystem failed with code ZX-19")
    assert result["diagnostics"][0]["id"] == "unknown"
    assert result["input_lines"] == 1


def test_empty_input_is_safe():
    result = diagnose_log(" \n")
    assert result["diagnostics"][0]["id"] == "unknown"
    assert result["input_lines"] == 0
