
library(httr)
library(jsonlite)
library(dplyr)
library(tidyr)
library(purrr)

# url <- 'https://models.ftntools.com/api/fantasy/projections_by_date?start_date=2025-03-30&end_date=2025-04-01&source=FTN&league=MLB&key=ftnmodelstesting'
url <- 'https://models.ftntools.com/api/fantasy/projections_by_date?start_date=2025-03-29&end_date=2025-03-29&source=FTN&league=MLB&key=ftnmodelstesting'

response <- GET(url)

json_data <- content(response, "text", encoding = "UTF-8")
parsed_data <- fromJSON(json_data, flatten = TRUE)

# Extract ID, name, and position
players_df <- parsed_data %>%
  select(id, name, position, projections) 

# Expand the projections column
expanded_projections <- players_df %>%
  mutate(projections = map(projections, ~{
    if (is.data.frame(.x)) {
      .x %>% pivot_wider(names_from = stat, values_from = value)
    } else {
      tibble()  # Return empty tibble if no projections
    }
  })) %>%
  unnest(projections, keep_empty = TRUE)

foo <- expanded_projections %>% 
  filter(!position %in% c('SP', 'RP', 'P', '')) %>% 
  mutate(hits = single + double + triple + homerun) %>% 
  mutate(ab = hits + out) %>% 
  filter(ab == 0)
  
  
# } else {
#   cat("No projections data available.\n")
# }
# 
# print(head(projections_df))

# df <- as.data.frame(parsed_data)



# allInfoDoc <- url %>% 
#   httr::GET(config = httr::config(ssl_verifypeer = FALSE)) %>% 
#   content(as = "text") %>% fromJSON()
