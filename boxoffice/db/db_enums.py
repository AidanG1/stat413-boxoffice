from enum import Enum


class CREATIVE_TYPE(str, Enum):
    DRAMATIZATION = "Dramatization"
    MULTIPLE_CREATIVE_TYPES = "Multiple Creative Types"
    SCIENCE_FICTION = "Science Fiction"
    FANTASY = "Fantasy"
    HISTORICAL_FICTION = "Historical Fiction"
    CONTEMPORARY_FICTION = "Contemporary Fiction"
    SUPER_HERO = "Super Hero"
    FACTUAL = "Factual"
    KIDS_FICTION = "Kids Fiction"


class GENRE(str, Enum):
    WESTERN = "Western"
    MULTIPLE_GENRES = "Multiple Genres"
    HORROR = "Horror"
    EDUCATIONAL = "Educational"
    MUSICAL = "Musical"
    DOCUMENTARY = "Documentary"
    BLACK_COMEDY = "Black Comedy"
    ADVENTURE = "Adventure"
    REALITY = "Reality"
    ACTION = "Action"
    THRILLER_SUSPENSE = "Thriller/Suspense"
    ROMANTIC_COMEDY = "Romantic Comedy"
    CONCERT_PERFORMANCE = "Concert/Performance"
    DRAMA = "Drama"
    COMEDY = "Comedy"


class MPAA_RATING(str, Enum):
    NR = "NR"
    PG = "PG"
    OPEN = "Open"
    G = "G"
    M_PG = "M/PG"
    NOT_RATED = "Not Rated"
    GP = "GP"
    NC_17 = "NC-17"
    PG_13 = "PG-13"
    R = "R"
    NOT_YET_RATED = "Not Yet Rated"


class PRODUCTION_METHOD(str, Enum):
    DIGITAL_ANIMATION = "Digital Animation"
    MULTIPLE_PRODUCTION_METHODS = "Multiple Production Methods"
    ANIMATION_LIVE_ACTION = "Animation/Live Action"
    LIVE_ACTION = "Live Action"
    ROTOSCOPING = "Rotoscoping"
    HAND_ANIMATION = "Hand Animation"
    STOP_MOTION_ANIMATION = "Stop-Motion Animation"


class SOURCE(str, Enum):
    BASED_ON_TV = "Based on TV"
    REMAKE = "Remake"
    BASED_ON_COMIC_GRAPHIC_NOVEL = "Based on Comic/Graphic Novel"
    BASED_ON_SHORT_FILM = "Based on Short Film"
    BASED_ON_SONG = "Based on Song"
    COMPILATION = "Compilation"
    ORIGINAL_SCREENPLAY = "Original Screenplay"
    BASED_ON_PLAY = "Based on Play"
    BASED_ON_RADIO = "Based on Radio"
    BASED_ON_TOY = "Based on Toy"
    BASED_ON_RELIGIOUS_TEXT = "Based on Religious Text"
    BASED_ON_MUSICAL_OR_OPERA = "Based on Musical or Opera"
    BASED_ON_THEME_PARK_RIDE = "Based on Theme Park Ride"
    BASED_ON_GAME = "Based on Game"
    BASED_ON_FOLK_TALE_LEGEND_FAIRYTALE = "Based on Folk Tale/Legend/Fairytale"
    BASED_ON_FICTION_BOOK_SHORT_STORY = "Based on Fiction Book/Short Story"
    BASED_ON_FACTUAL_BOOK_ARTICLE = "Based on Factual Book/Article"
    BASED_ON_WEB_SERIES = "Based on Web Series"
    BASED_ON_BALLET = "Based on Ballet"
    SPIN_OFF = "Spin-Off"
    BASED_ON_REAL_LIFE_EVENTS = "Based on Real Life Events"
    BASED_ON_MOVIE = "Based on Movie"
    BASED_ON_MUSICAL_GROUP = "Based on Musical Group"
