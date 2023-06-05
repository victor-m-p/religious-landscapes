# Extract answers of questions of interest

# Load data
data <- fread("../data/raw/drh.csv")

# Extract group entries only
data_group <- data[Poll == "Religious Group (v6)" | Poll == "Religious Group (v5)"]

# Create questions of interest vector
# There are 2 different "Done to enforce group norms:" with the parent questions "Is the reason for supernatural punishment known:" and "Is the cause/purpose of supernatural rewards known:"
questions <- c("Is there violent conflict (within sample region):", 
               "Is there violent conflict (with groups outside the sample region):",
               "Does the religious group actively proselytize and recruit new members:", 
               "Is religious observance enforced by the polity:",
               "Are apostates prosecuted or punished:",
               "Are they written:",
               "Are there formal institutions (i.e. institutions that are authorized by the religious community or political leaders) for interpreting the scriptures:",
               "Is monumental religious architecture present:",
               "Mass gathering point [plazas, courtyard, square. Places permanently demarcated using visible objects or structures]:",
               "Are pilgrimages present:",
               "Belief in afterlife:",
               "Reincarnation linked to notion of life-transcending causality (e.g. karma):",
               "Human sacrifices present:",
               "A supreme high god is present:",
               "There is supernatural monitoring of prosocial norm adherence in particular:",
               "Supernatural beings care about sex:",
               "Supernatural beings care about honouring oaths:",
               "Supernatural beings care about performance of rituals:",
               "Supernatural beings care about conversion of non-religionists:",
               "Done to enforce group norms:",
               "Supernatural punishments are meted out in the afterlife:",
               "Supernatural punishments are meted out in this lifetime:",
               "Supernatural rewards are bestowed out in the afterlife:",
               "Supernatural rewards are bestowed out in this lifetime:",
               "Are messianic beliefs present:",
               "Are general social norms prescribed by the religious group:",
               "Is there a conventional vs. moral distinction in the religious group:",
               "Does membership in this religious group require celibacy (full sexual abstinence):",
               "Does membership in this religious group require constraints on sexual activity (partial sexual abstinence):",
               "Does membership in this religious group require forgone food opportunities (taboos on desired foods):",
               "Does membership in this religious group require permanent scarring or painful bodily alterations:",
               "Does membership in this religious group require sacrifice of property/valuable items:",
               "Does membership in this religious group require sacrifice of time (e.g., attendance at meetings or services, regular prayer, etc.):",
               "Does membership in this religious group require accepting ethical precepts:",
               "Does membership in this religious group require participation in small-scale rituals (private, household):",
               "Does membership in this religious group require participation in large-scale rituals:",
               "Are extra-ritual in-group markers present:")

# Select questions of interest
group_qoi <- data_group[Question %in% questions][
  , list(`Entry ID`, `Entry name`, `Question ID`, Question, `Parent question`, Answers, `Parent answer`)][
    Answers != "Field doesn't know" & Answers != "I don't know"]

# Extract missing parent questions
parent_qoi <- data_group[Question %in% group_qoi$`Parent question`][
  , list(`Entry ID`, `Entry name`,`Question ID`, Question, `Parent question`, Answers, `Parent answer`)][
    Answers != "Field doesn't know" & Answers != "I don't know"]

# Combine questions of interest and parent questions and filter "Field doesn't know" and "I don't know" answers
all_qoi <- rbind(group_qoi, parent_qoi)

# Create missing questions
complete_qoi <- all_qoi %>%
  complete(nesting(`Entry ID`, `Entry name`),
           nesting(Question, `Question ID`, `Parent question`),
           fill = list(value = 0)) %>%
  filter(!is.na(`Question ID`)) %>%
  # Remove questions without parent questions
  filter(!(is.na(Answers) & `Parent question` == ""))

# Extract unanswered child questions 
unans_qoi <- complete_qoi %>%
  filter(is.na(Answers) & `Parent question` != "") %>%
  select(-`Parent answer`) %>%
  # Prevent questions with answers from being included
  anti_join(group_qoi, by = join_by(`Entry ID`, `Entry name`, Question, `Question ID`, `Parent question`))

# Extract parent questions with No answers and rename variables for joining
parent_qoi_no <- complete_qoi %>% 
  filter(Question %in% unans_qoi$`Parent question`) %>%
  filter(Answers == "No") %>%
  select(`Entry ID`, `Entry name`, Question, Answers) %>%
  rename(`Parent question` = Question, `Parent answer` = Answers) 
  
# If parent question has a no answers replace the answer of the corresponding child question
filled_qoi <- parent_qoi_no %>%
  right_join(unans_qoi, by = join_by(`Entry ID`, `Entry name`, `Parent question`)) %>% 
  mutate(Answers = ifelse(is.na(Answers), `Parent answer`, Answers)) %>%
  filter(!is.na(`Parent answer`)) %>%
  select(-`Parent answer`) %>%
  distinct() %>%
  anti_join(group_qoi, by = join_by(`Entry ID`, `Entry name`, `Parent question`, Question, `Question ID`,
                                    Answers))

# Join filled question/answers with answered data
data_filled <- bind_rows(group_qoi, filled_qoi) %>%
  select(-`Parent answer`) 

# Select variables for saving
answers <- data_filled %>%
  select(`Entry ID`, `Question ID`, Answers)

# Extract questions of interest's names
questions_names <- group_qoi %>%
  select(`Question ID`, Question) %>%
  distinct()

# Save question data
write_csv(answers, "../data/preprocessing/answers.csv")
write_csv(questions_names, "../data/preprocessing/questions.csv")
