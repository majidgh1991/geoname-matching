import jaro
from LabelGeonames import SmithWaterman

print jaro.metric_jaro_winkler("sanofiaventisusllcus", "sanofiaventisdeutschlandgmbh")

ss = SmithWaterman(1, "")
ss.measure("", "")


