library(BayesianFirstAid)
library(ggplot2)
library(ggthemes)

#
# Show a single image, match negatively valenced emotions (angry and sad)
#

shaemo.neg <- read.csv("../data/study_1/shape_emotion_negative.csv", header=TRUE, sep=",")
shaemo.neg <- shaemo.neg[shaemo.neg$exclude == 0,]
shaemo.neg.congruent <- sum(shaemo.neg$congruent)

##
# Binomial test across all images and sounds
shaemo.neg.bayes.test <- bayes.binom.test(shaemo.neg.congruent, nrow(shaemo.neg), p = 0.5)
plot(shaemo.neg.bayes.test)



#
# Play a single sound, click on the emotion that matches the sound
#
souemo.neg <- read.csv("../data/study_1/sound_emotion_negative.csv", header=TRUE, sep=",")
souemo.neg.congruent <- sum(souemo.neg$congruent)

##
# Binomial test for congruent/incongruent total merged across all images and sounds

souemo.neg.bayes.test <- bayes.binom.test(souemo.neg.congruent, nrow(souemo.neg), p = 0.5)
plot(souemo.neg.bayes.test)



#
# Shape-emotion, excited-peaceful
#

shaemo.pos <- read.csv("../data/study_1/shape_emotion_positive.csv", header=TRUE, sep=",")

# Get exclusions
shaemo.pos <- shaemo.pos[shaemo.pos$exclude!=1,]

# Identify congruent vs. incongruent responses
shaemo.pos$congruent <- 0
shaemo.pos[shaemo.pos$excited==1 & (shaemo.pos$shape=='spiky-1' | shaemo.pos$shape=='spiky-2'),]$congruent <- 1
shaemo.pos[shaemo.pos$excited==0 & (shaemo.pos$shape=='rounded-1' | shaemo.pos$shape=='rounded-2'),]$congruent <- 1
shaemo.pos.congruent <- sum(shaemo.pos$congruent)

# Bayesian binomial test
shaemo.pos.bayes.test <- bayes.binom.test(shaemo.pos.congruent, nrow(shaemo.pos), p = 0.5)
plot(shaemo.pos.bayes.test)



#
# Sound-emotion, excited-peaceful
#

souemo.pos <- read.csv("../data/study_1/sound_emotion_positive.csv", header=TRUE, sep=",")

# Get exclusions
souemo.pos <- souemo.pos[!(souemo.pos$exclude==1 & !is.na(souemo.pos$exclude)),]

# Identify congruent vs. incongruent responses
souemo.pos$congruent <- 0
souemo.pos[souemo.pos$excited==1 & souemo.pos$sound=='noise',]$congruent <- 1
souemo.pos[souemo.pos$excited==0 & souemo.pos$sound=='sine',]$congruent <- 1
souemo.pos.congruent <- sum(souemo.pos$congruent)

# Bayesian binomial test
souemo.pos.bayes.test <- bayes.binom.test(souemo.pos.congruent, nrow(souemo.pos), p = 0.5)
plot(souemo.pos.bayes.test)



# Figure, Study 1

fig.est <- c(
  souemo.neg.bayes.test$stats["theta", "median"],
  souemo.pos.bayes.test$stats["theta", "median"],
  shaemo.neg.bayes.test$stats["theta", "median"],
  shaemo.pos.bayes.test$stats["theta", "median"]
)
fig.HDIlo <- c(
  souemo.neg.bayes.test$stats["theta", "HDIlo"],
  souemo.pos.bayes.test$stats["theta", "HDIlo"],
  shaemo.neg.bayes.test$stats["theta", "HDIlo"],
  shaemo.pos.bayes.test$stats["theta", "HDIlo"]
)
fig.HDIup <- c(
  souemo.neg.bayes.test$stats["theta", "HDIup"],
  souemo.pos.bayes.test$stats["theta", "HDIup"],
  shaemo.neg.bayes.test$stats["theta", "HDIup"],
  shaemo.pos.bayes.test$stats["theta", "HDIup"]
)
fig.desc <- c(
  "Sound, neg.",
  "Sound, pos.",
  "Shape, neg.",
  "Shape, pos."
)

fig.bayes <- data.frame(est = fig.est, HDIlo = fig.HDIlo, HDIup = fig.HDIup)
fig.bayes$desc <- factor(fig.desc, levels = fig.desc[c(1,2,3,4,5,6)])
fig.plot <- ggplot(fig.bayes, aes(desc, est, ymin = HDIlo, ymax = HDIup)) + 
  scale_y_continuous(breaks = seq(from = 0.4, to = 1.0, by = 0.1)) + 
  geom_pointrange() + 
  labs(
    title = "",
    x = "",
    y = "% Congruent") + 
  theme_tufte(ticks=TRUE, base_size = 16, base_family = "Helvetica") +
  theme(axis.title.x = element_text(vjust = -0.2), axis.title.y = element_text(vjust = 1.2)) +
  theme(plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")) + 
  geom_hline(yintercept = 0.5, col="gray", linetype = "dashed", lwd=0.5) + 
  annotate("text", x=0.4, y=0.505, label="(chance)", color="gray", hjust=0, vjust=0, size=4.0) 
fig.plot

