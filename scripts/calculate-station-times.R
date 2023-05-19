library (gtfsrouter)
packageVersion ("gtfsrouter")
library(lubridate)
library('plyr')
library('dplyr')
library('stringr')

gtfs <- extract_gtfs (
    filename="/Users/bmorris/github/gmt-isochrones/data/ccta-vt-us.zip"
)

gtfs <- gtfs_timetable (gtfs, day = "Wed")

stops <- read.csv("/Users/bmorris/github/gmt-isochrones/data/ccta_vt_us/stops.txt")

for (stop_id in stops$stop_id) {
    print(paste0('Processing data for stop ', stop_id))
    x <- gtfs_traveltimes (
        gtfs,
        from = stop_id,
        from_is_id = TRUE,
        start_time_limits = c (12, 14) * 3600,
        max_traveltime = 60 * 60 * 4,
    )
    x$duration <- period_to_seconds(hms(x$duration))
    write.csv(x, paste0("/Users/bmorris/github/gmt-isochrones/data/durations/",stop_id, ".csv"), row.names=FALSE)
  
}
