NAMES <- read.table("Disaster_clean_final.csv", nrow = 1, stringsAsFactors = FALSE, sep = ",")
DATA <- read.table("Disaster_clean_final.csv", skip = 1, fill=TRUE, stringsAsFactors = FALSE, sep = ",")
DATA <- DATA[, 1:27]
names(DATA) <- NAMES 
plot(DATA$`MUNICIPAL COSTS`)
plot(DATA$`UTILITY - PEOPLE AFFECTED`)
plot(DATA$`UTILITY - PEOPLE AFFECTED`)
plot(DATA$`OGD COSTS`)
plot(DATA$MAGNITUDE)


