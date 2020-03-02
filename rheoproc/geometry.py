
def get_geometry(hw_version=-1):
    GEOMETRY = [
            (20190101, { 'RIN': 0.01505, 'ROUT': 0.01975 })
            ]

    hw_version = int(hw_version)

    if hw_version == -1:
        return GEOMETRY[-1][1]

    for hw, geom in reversed(GEOMETRY):
        if hw <= hw_version:
            return geom

    raise Exception("No suitable geometry found!")
