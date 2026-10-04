# Design Changes

This file covers the site's styling. The first section is the look I set up earlier, and the rest are my changes for Problem 10, "Style the website." The look stays the same throughout: Yale navy and bright gold, a serif display font for headlines, rounded cards, and a little motion. It works on a phone, and animation switches off for "reduce motion."

**The colors and type I used**

| What | Value | Where I used it |
|---|---|---|
| Yale navy | `#00356B` (with a darker `#00244A`) | Banners, headers, buttons, headlines |
| Bright gold | `#F2B705` | Tags, badges, borders, highlights, the active map pin |
| Red, green, purple | Soft accents | Category colors on Explore tags and map pins |
| Serif display font | Iowan Old Style / Palatino / Georgia | Headlines and big numbers |
| Sans-serif body font | The system font | Everything else |

## The foundation: the look before Problem 10

**Overall look and feel**
- Clean and professional like the Yale website, in Yale navy instead of the purple default.
- I added bright gold, a serif headline font, and small animations because it was too plain. Pages fade up as they load, and the favicon is a navy "CC".

**Navigation bar**
- Sticky white bar with a gold line under it, a gold star that spins on hover, and a gold underline on the active page.
- **Create account** is a gold button with a 3D shadow. Signed-in shoppers see "Hi, {name}" and **Log out**.

**Home page**
- Navy hero with a gold tag, a large serif headline, and a gold **Browse the collection** button.
- A Harkness Tower photo sits behind a navy gradient so the text stays readable.
- A frosted-glass row of category chips overlaps the hero's bottom edge, followed by three tilted cards that lift on hover.
- I removed the floating circles, the diagonal edge, and a scrolling gold ticker.

**Inner pages**
- Page headings have a gold highlighter stripe behind them.
- Log in and Create account share a narrow card with focus rings, red-edged errors, and a password checklist that turns green. A pale-yellow banner reminds people to update a weak password.

## 1. About Us: adding personality

The About Us page used to be a title and two paragraphs. I rebuilt it with six sections:

- **A navy hero banner.** A gold glow, a gold tag, a big serif headline ("Bulldog pride, made easy to wear."), and my intro line. On the right is a collage of five real products on white cards, each at a slight angle. They straighten and lift on hover and link to their product pages.
- **"The short version."** A large gold-edged statement ("From the first week on campus to the last reunion.") beside my two paragraphs, which I kept exactly as I wrote them.
- **"What we are about."** Three tilted cards with gold tops and big faded numbers.
- **"By the numbers."** A navy band with four count-up numbers (styles, item types, residential colleges, sports) that come from the live catalogue.
- **"Shop your way."** Three steps in gold circles: Browse, Ask, and Find your size.
- **A call to action.** "Ready to rep the Bulldogs?" with a gold **Browse the collection** button and an **Ask the assistant** button that opens the chat panel.

I didn't invent any history, founders, or dates.

**A readability fix.** The **Ask the assistant** button first showed as white text on a light gray box, nearly impossible to read. The outlined style had no background, so the browser's default gray took over. I made it transparent, so it's now a white outline and white text on navy, about 12 to 1 contrast.

## 2. The Personal Assistant: a Bill Clinton-inspired character

I gave the assistant a Bill Clinton-inspired persona. Only the assistant has it; the rest of the site stays the same.

### The voice

I rewrote the voice section of the assistant's prompt. The character is a warm, folksy charmer with relentless optimism, a love of numbers, and a running saxophone joke. A few signature lines:

- A sold-out size: "I feel your pain, friend… let's build a bridge to a size that works."
- A price: "Now, I'm a numbers fella…"
- Browsing results: "There's no filibuster here."
- Politics bait: "I'd give you a stump speech, but my only platform is fleece."
- A returning shopper: "Welcome back, Comeback Kid."

The jokes never change a fact. Prices, stock, and colors still come only from the database.

### Framing him as a Yale alum

The character is a proud Yale Law alum, since the real Bill Clinton earned his law degree there (J.D., class of 1973). You'll see "Yale Law, class of '73 energy" and "once a Bulldog, always a Bulldog." If someone asks whether it went to Yale, it says it's an AI that didn't attend, but the man it's channeling did. It never invents personal memories.

### Keeping it a parody

- The chat window always shows: "A playful AI persona inspired by Bill Clinton, a Yale Law alum. Not the real Bill Clinton, and not endorsed by him."
- If asked, it says plainly that it's an AI doing a bit. It won't invent quotes and avoids politics and controversy.
- If someone sounds in crisis, it drops the character and responds with care.

### How the chat window looks

- **Header.** A navy gradient with a round portrait in a gold ring, a small gold saxophone badge, and the line "The Comeback Kid · a Yale Law alum-inspired AI."
- **The portrait.** The official White House photo by Bob McNeely (public domain). I first had it pop up over the window, which cut his face off, so I moved it inside the header.
- **A campaign stripe.** A red, white, and blue band under the header, above the italic disclaimer on a cream strip. Assistant bubbles have a gold stripe on the left.
- **Starter buttons.** Four campaign-plank buttons: The Hoodie Platform, Gifts under $50, Size check, and Surprise me. They disappear once the conversation starts.
- **While it thinks.** Bouncing music notes and a line like "Warming up the saxophone…" The chat button is a saxophone icon.
- **The greeting.** Guests get "Well, hello there, friend!" Signed-in shoppers are greeted by first name, and returning ones as the Comeback Kid.

## 3. The Explore tab

I added an **Explore** tab between Products and About Us. It's a fun tour of iconic spots on and around campus, with one catalogue item suggested to wear at each.

### The stops and the outfits

- **16 stops:** Old Campus, Connecticut Hall, Harkness Tower, Sterling Memorial Library, the Beinecke Library, Woolsey Hall, the Yale University Art Gallery, the Yale Center for British Art, the Peabody Museum, the School of Management, Rudolph Hall, the Divinity School, Kroon Hall, the Yale Bowl, Ingalls Rink, and Frank Pepe Pizzeria.
- **Categories.** Each stop has a colored tag: Landmarks (6), Museums (3), Schools (4), Sports (2), and New Haven (1).
- **One outfit per stop.** Each stop pairs a different product with a short reason ("Navy is forgiving of any white clam pie mishaps."). The card shows the photo, name, price, and sizes in stock, and clicking it goes to the product page.

I started with 20 stops, but photo downloads were rate-limited, so I dropped four (Yale Law School, Payne Whitney Gymnasium, the New Haven Green, and Toad's Place).

### A single slideshow

- **The photos.** Free-licensed Wikimedia Commons photos at 2,400 pixels wide. Every slide credits the photographer and license, with a link.
- **Moving through it.** Arrow buttons, a numbered counter, keyboard arrows, swiping, and a strip of 16 thumbnails. It wraps around at either end.
- **A Play button.** Autoplay is off by default, pauses on hover, and never runs for people who want less motion. A gold **Surprise me** button jumps to a random stop.
- **Shareable and accessible.** The address changes with each stop (like `?stop=harkness-tower`), and screen readers hear "Stop 3 of 16: Harkness Tower."

### The layout and the map

The slideshow takes the left 70% of the screen, and a campus map takes the right 30%:

- **A real map.** OpenStreetMap, starting on central campus.
- **16 numbered pins** colored by category: navy landmarks, red museums, gold schools, green sports, and purple New Haven.
- **Linked to the slideshow.** Clicking a pin jumps to that stop. As you move through the slides, the matching pin turns gold, grows, and pulses.
- **The Yale Bowl.** It's a few miles west of campus, so the starting view leaves it out. **Show all stops** fits every pin, and **Campus** returns to the start.
- **On a phone.** The map moves below the slideshow.

The pin locations are approximate.

## 4. The footer

- **A credit.** "Website by **Isha Shah**" on the bottom bar of every page, with my name in bold gold.
- **One font.** My name was in the serif headline font, larger and letter-spaced, next to sans-serif text. I standardized the bar to one font in two sizes.
- **The other credits.** The bar also credits the home photo and the assistant's portrait, and notes the assistant is a parody.

## Where the photo credits come from

Most Explore photos are Creative Commons, so each slide names the photographer and license. A few are public domain, and I credit them anyway.
