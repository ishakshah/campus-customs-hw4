// The Explore slideshow: iconic spots on and around the Yale campus, each with a photo and one item from the
// catalogue to wear there. `productId` must be a product_id from the catalogue. Photos are in public/explore/
// (large) and public/explore/thumbs/ (small), named after the spot's id.

export type ExploreCategory = 'Landmarks' | 'Museums' | 'Sports' | 'Schools' | 'New Haven'

export interface PhotoCredit {
  author: string
  license: string
  /** The photo's file name on Wikimedia Commons, used to link back to its page. */
  file: string
}

export interface ExploreSpot {
  id: string
  name: string
  /** Where the pin goes on the map (approximate). */
  lat: number
  lng: number
  category: ExploreCategory
  /** A line about the place. */
  about: string
  /** Why this item suits the place. */
  why: string
  productId: string
  credit: PhotoCredit
}

export const photoUrl = (spot: ExploreSpot) => `/explore/${spot.id}.jpg`
export const thumbUrl = (spot: ExploreSpot) => `/explore/thumbs/${spot.id}.jpg`
export const creditUrl = (credit: PhotoCredit) =>
  `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(credit.file.replace(/ /g, '_'))}`

// In tour order, roughly from Old Campus out to the stadium and into town.
export const EXPLORE_SPOTS: ExploreSpot[] = [
  {
    id: 'old-campus',
    lat: 41.3085,
    lng: -72.9285,
    name: 'Old Campus',
    category: 'Landmarks',
    about: 'The brick-and-ivy quad where first-years live, through Phelps Gate, with plenty of frisbee.',
    why: 'The classic Yale hoodie, because every Old Campus afternoon needs one.',
    productId: 'basic-hoodie-big-yale',
    credit: { author: 'VillageHero', license: 'CC BY-SA 2.0', file: 'Yale University old campus with Harkness tower 2 (44517914954).jpg' },
  },
  {
    id: 'connecticut-hall',
    lat: 41.308125,
    lng: -72.92948,
    name: 'Connecticut Hall',
    category: 'Landmarks',
    about: 'The oldest surviving building on campus, with the Nathan Hale statue standing out front.',
    why: 'The oldest building on campus deserves a classic crest crewneck.',
    productId: 'super-heavyweight-crewneck-arched-yale-crest',
    credit: { author: 'Pascal Walschots', license: 'CC BY 2.0', file: 'Connecticut Hall Yale from north.jpg' },
  },
  {
    id: 'harkness-tower',
    lat: 41.3093,
    lng: -72.9294,
    name: 'Harkness Tower',
    category: 'Landmarks',
    about: 'The Gothic tower at the Memorial Quadrangle, whose carillon bells ring out over campus.',
    why: 'Branford and Saybrook live in its shadow, so rep your college in a quarter-zip.',
    productId: 'branford-1-4-zip',
    credit: { author: 'ajay_suresh', license: 'CC BY 2.0', file: 'Harkness Tower - Yale University (54106458290).jpg' },
  },
  {
    id: 'sterling-library',
    lat: 41.3113,
    lng: -72.9291,
    name: 'Sterling Memorial Library',
    category: 'Landmarks',
    about: "Yale's cathedral-like main library, all stone, stained glass, and hush.",
    why: 'Long study sessions call for a heavyweight crewneck you can sink into.',
    productId: 'champion-reverse-weave-crewneck',
    credit: { author: 'Christian David', license: 'CC BY-SA 4.0', file: 'Sterling Memorial Library seen from the front, Yale University, New Haven, Connecticut.jpg' },
  },
  {
    id: 'beinecke',
    lat: 41.31161,
    lng: -72.92722,
    name: 'Beinecke Rare Book & Manuscript Library',
    category: 'Landmarks',
    about: 'Its marble panels turn translucent, glowing like amber when the sun hits them.',
    why: 'A cream tee to match the glow.',
    productId: 't-felt-y-heavyweight',
    credit: { author: 'Karlfonza', license: 'CC BY-SA 4.0', file: 'Beinecke Rare Book & Manuscript Library.jpg' },
  },
  {
    id: 'woolsey-hall',
    lat: 41.31111,
    lng: -72.92583,
    name: 'Woolsey Hall',
    category: 'Landmarks',
    about: 'The grand domed concert hall, famous for its enormous Newberry Memorial Organ.',
    why: 'Dress up a little for concert night in a sharp bomber.',
    productId: 'brooks-brothers-bomber-jacket-yale',
    credit: { author: 'ajay_suresh', license: 'CC BY 2.0', file: 'Woolsey Hall - Yale University (54106457850).jpg' },
  },
  {
    id: 'art-gallery',
    lat: 41.308459,
    lng: -72.930985,
    name: 'Yale University Art Gallery',
    category: 'Museums',
    about: 'The oldest university art museum in the Western Hemisphere, and it is free to visit.',
    why: 'A gallery-ready mockneck that looks like it belongs in the collection.',
    productId: 'yale-maplehouse-diana-mockneck',
    credit: { author: 'Ragesoss', license: 'Public domain', file: 'Yale University Art Gallery exterior.jpg' },
  },
  {
    id: 'british-art',
    lat: 41.307908,
    lng: -72.930906,
    name: 'Yale Center for British Art',
    category: 'Museums',
    about: "Louis Kahn's last building, home to the largest collection of British art outside the UK.",
    why: 'A cozy fleece for a quiet afternoon among the paintings.',
    productId: 'berkeley-sweater-fleece-jacket',
    credit: { author: 'ajay_suresh', license: 'CC BY 2.0', file: 'Yale Center for British Art (54106458295).jpg' },
  },
  {
    id: 'peabody',
    lat: 41.3158,
    lng: -72.921,
    name: 'Peabody Museum of Natural History',
    category: 'Museums',
    about: 'Dinosaur skeletons and the famous Age of Reptiles mural.',
    why: 'Bring the whole crew, cousins included, in the family favorite.',
    productId: 'yale-cousin-crewneck',
    credit: { author: 'ajay_suresh', license: 'CC BY 2.0', file: 'Yale Peabody Museum (54106346944).jpg' },
  },
  {
    id: 'school-of-management',
    lat: 41.315278,
    lng: -72.920278,
    name: 'Yale School of Management',
    category: 'Schools',
    about: 'Where future business leaders sharpen their pitches.',
    why: 'Casual-Friday ready, with a crest.',
    productId: 'school-of-management-crest-t-shirt',
    credit: { author: 'Nick Allen', license: 'CC BY-SA 3.0', file: 'Yale School of Management Evans Hall front.JPG' },
  },
  {
    id: 'rudolph-hall',
    lat: 41.3087,
    lng: -72.9319,
    name: 'Rudolph Hall (School of Architecture)',
    category: 'Schools',
    about: 'A bold concrete landmark designed by Paul Rudolph for the architecture school.',
    why: 'A clean, structured crewneck for a building that loves clean lines.',
    productId: 'school-of-architecture-crewneck',
    credit: { author: 'Kenneth C. Zirkel', license: 'CC BY-SA 4.0', file: 'Rudolph Hall and Loria Center, Yale School of Architecture.jpg' },
  },
  {
    id: 'divinity-school',
    lat: 41.323333,
    lng: -72.921389,
    name: 'Yale Divinity School',
    category: 'Schools',
    about: 'A hilltop campus and Marquand Chapel on Prospect Street.',
    why: 'Hilltop breezes call for a good fleece.',
    productId: 'divinity-school-fleece-sweater',
    credit: { author: 'Carol M. Highsmith', license: 'Public domain', file: 'Yale Divinity School Highsmith.jpg' },
  },
  {
    id: 'kroon-hall',
    lat: 41.316932,
    lng: -72.924145,
    name: 'Kroon Hall (The Forest School)',
    category: 'Schools',
    about: 'Home of the Yale School of the Environment, the school that grew out of the old Forest School.',
    why: 'An outdoorsy hoodie for a building that loves the outdoors.',
    productId: 'the-forest-school-hoodie',
    credit: { author: 'Sage Ross', license: 'CC BY-SA 3.0', file: 'Kroon Hall exterior - 1.jpg' },
  },
  {
    id: 'yale-bowl',
    lat: 41.313,
    lng: -72.96,
    name: 'The Yale Bowl',
    category: 'Sports',
    about: 'Where Yale football plays, and where The Game against Harvard comes to town every other year.',
    why: 'Game day demands the Harvard-Yale tee.',
    productId: '2025-yale-vs-harvard-t-shirt',
    credit: { author: 'Kenneth C. Zirkel', license: 'CC BY 4.0', file: 'Yale Bowl 50 Yard Line.jpg' },
  },
  {
    id: 'ingalls-rink',
    lat: 41.316552,
    lng: -72.925039,
    name: 'Ingalls Rink',
    category: 'Sports',
    about: 'Known as "The Whale" for its sweeping curved roof, and home to Yale hockey.',
    why: 'Rinks run cold, so bring the hockey hoodie.',
    productId: 'yale-sports-hoodie-hockey',
    credit: { author: 'Quintin Soloviev', license: 'CC BY 4.0', file: 'Ingalls Ice Rink (Yale Hockey).jpg' },
  },
  {
    id: 'pepes',
    lat: 41.302907,
    lng: -72.916933,
    name: 'Frank Pepe Pizzeria',
    category: 'New Haven',
    about: 'The home of New Haven-style apizza and its famous white clam pie, usually with a line out the door.',
    why: 'Navy is forgiving of any white clam pie mishaps.',
    productId: 'crew-left-chest-hoodie',
    credit: { author: 'ajay_suresh', license: 'CC BY 2.0', file: 'Frank Pepe Pizzeria Napoletana (54106004336).jpg' },
  },
]

/** The Yale Bowl is a few miles west of campus, so the map's starting view leaves it out. Tap its pin or "Show all". */
export const FAR_AWAY_SPOT_ID = 'yale-bowl'
