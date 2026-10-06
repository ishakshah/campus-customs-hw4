# AI Prompts — HW4

A word-for-word log of every prompt typed for this homework, organized by problem.

## Problem 1: Vibe coder prompts

### Prompt 1

Today we're working exclusively in the @hw4 folder. Make sure you can access it, and can you view the data file in there?

### Prompt 2

Okay, for this hw4 make sure you've put a Python venv there. then create AI_prompts.md in @hw4 . This md file will store every prompt I ask of you, can you word for word store everything I type in here for this hw? Structure it by problem. Put everything for this hw so far unde rProblem 1: Vibe coder prompts

### Prompt 3

[Image attached: screenshot of the expected submission zip layout]

And for hw submission, this will be the expected zip layout. Make sure during this hw we're on track for this and flag if not:

### Prompt 4

yes, follow the submission layout, you can delete data.zip now, and exclude venv from the submission later

### Prompt 5

So today we're building a customer website with a chatbot for Campus Customes. This entails a React + Vite Typescript front end and a Python FastAPI backend, with a PdyanticAI agent brain. We will use my PORTKEY_API_KEY for any AI model calls, ok? Let's use the gpt 5.6 luna model for the easier-lift commands and the gpt 6 astra model for the heavier-lift prompts. Start with 5.6 and if a command looks like heavier-lift, ask me if we want to switch to 6. For submission, I will publish this project to my public Github repo and submit the repo URL with the file tree I showed you earlier. Understand the context?

### Prompt 6

yes, it's gpt-6-astra. Oh and for site colors, look at https://yalebulldogblue.com/ to understand the aesthetic I want, I don't want the Justin Bieber look that's the default currently. I want it to look clean, modern, and professional. like the yale website

## Problem 2: Analyze the database

### Prompt 7

Let's move onto Problem 2: Analyze the databse. Look at @hw4/data/campus_customs.db and give me an overview of the fields of each table

### Prompt 8

Now, start the file output/harness.md. In here, can you put each of the 4 tables and its fields. For each field, include one short line (5-15 words) on why each field is relevant for a campus apparel shop

## Problem 3: Build the Campus Customs website

### Prompt 9

Okay, onto Problem 3: Build the Campus Customs website. We're going to scaffold a React + Vite + Typescript front end for Campus Customs. have everything you need for this?

### Prompt 10

Yes, go ahead and with scaffolding the React + Vite + Typescript front end for Campus Customs and create hw4/frontend . Put a navigation bar at the top that links to these pages: Home, Products, About Us, Log in, Create account. For wording choices, pull Campus Customs-style wording from yalebulldogblue.com for Home and About Us. I will want to reword it, so ask me how.

### Prompt 11

[Answers selected in response to my questions about rewording the Home and About Us copy]

- What tone should the reworded Home and About Us copy have? → More polished and professional
- Which parts of the copy do you want to reword? → Everything

### Prompt 12

Can you confirm content.ts updated with my edits and I didn't mess anything up?

### Prompt 13

check one more time

### Prompt 14

Next step, on the Products page, pull product images from the catalogue by using the image paths in the database. Also pull basic product info such as name, price, and a short description of the product (the description field in the catalogue is fine to use here). Make each product open a single-item page (with a large image on the left and the full product text on the right with description/price/sizes/stock if we have them). Click a product card on Products should take the shopper there to the single-item page. Also, add a chat interface in the bottom right corner of the site, it should look like a floating chat panel. This will be our Personal Assistant. We'll call the backend for that later. Lastly, to read the database, start a simple FastAPI app in backend/main.py just to serve products and images. In problem 5, we'll grow it into the agent backend

### Prompt 15

why does python3.13 need access to my Desktop folder?

### Prompt 16

Can I see the website yet?

### Prompt 17

Can we change the localhost URL? I also want to add some pizzazz to the website, it's too clean/professional. And change the headline from "Yale apparel, thoughtfully made", to "Yale apparel, for the Bulldog community"

### Prompt 18

[Answer selected in response to my question about changing the localhost URL]

- How do you want to change the localhost URL? → Friendly hostname (Recommended)

### Prompt 19

I don't like the rotating yellow headline thing on the front page. Can we change that to make something more modern? And the front page needs a better picture than this simple blue background picture, can you put a really nice picture of Yale campus?

### Prompt 20

[Answer selected in response to my question about which Yale campus photo to download]

- May I download a Yale campus photo from Wikimedia Commons into hw4/frontend/public/? Which one? → Harkness Tower Canopy (Recommended)

### Prompt 21

Some products on the product page are not a perfect square picture, so they have a background and then a border around that background, for exmaple the Berkeley 1 4 Zip. Can you change it so the border matches the background?

### Prompt 22

Also, if a product is titled "1 4 Zip", I want to change that to Quarter-Zip, in both the front and back end. Do the same with "T Shirt", I want that to read as T-Shirt. Also on the products page, some of the text gets cut off. I don't want the description under the photo. Can you make it so only the product title and price is under each product photo. When I hover over the photo, a transparent thing the size of the product photo will pop up with the product description. If the description is too long for the whole thing, shorten it. I don't want any runons like "..."

### Prompt 23

how come some products say "More details coming soon?"

### Prompt 24

Please write real descriptions for those 3, write them into a small file

### Prompt 25

To confirm, none of the products say "More details coming soon" anymore, right?

### Prompt 26

Okay, are we all good with problem 4?

### Prompt 27

i mean problem 3

## Problem 4: Create account and login

### Prompt 28

Ok onto problem 4: Create account and login. We're going to build a normal create-account / login flow. For create account, ask the user for these fields: first name, last name, email, and password. For password, ask them to enter it twice to "Confirm password". For logging in, we just need to ask for email and password. New accounts, when created, should be added to the users table. Store passwords securely - use a slow hash and add a salt.

### Prompt 29

is there anything else you'd recommend to protect safety of user data / passwords?

### Prompt 30

ill come back to this later. im trying to log in as the test user in the seed data base (email is test@campuscustoms.yale.edu) why isnt it working

### Prompt 31

Im inputting the password correctly but it's still saying incorrect email or password

### Prompt 32

It works now! I also just created an account, can you check it was done correctly on the backend. it looked good on the front end

### Prompt 33

Great! Now add onto output/harness.md with how authorization works. Include what we store for a user and how passwords are protected.

## Problem 5: PydanticAI agent backend

### Prompt 34

Yeah, prompt me again when I updated password requirements later. ok now onto Problem 5: PydanticAI agent backend. We're now going to build that shop chatbot as a PydanticAI agent behind Fast API, plugged into the front-end chat widget. can you put the API app in backend/main.py (this is the file we run with Uvicorn). Keep the agent as these 4 files next to it: 1) backend/prompts/prompt.md (system prompt; we will grow this file later) 2) backend/agent.py (agent entry/wiring), 3) backend/tools.py (tools the agent can call) and 4) backend/models.py (PydanticAI structured types). if you suggest retroactively adding anything to any of these files, let me know

### Prompt 35

so anything left to fix or can we move on? if nothing to fix, in main.py, can you expose a chat route so a message from the website returns a reply from the agent (and anything else you think we need for products / authorization). Confirm the agent is using my AI model API key

### Prompt 36

No, next put Campus Customes voice and safety basics into prompts/prompt.md. Start or udpate types in models.py for chat replies and product cards as needed. I want the backend to run from the backend folder like this: uvicorn main:app --reload --port 8000

### Prompt 37

i got this error zsh: command not found: uvicorn

### Prompt 38

sweet! now in @hw4/output/harness.md can you make a note of how the front end talks to FastAPI and how the agent is loaded (including prompt file and model). write it so it sounds like me

## Problem 6: Tools: product info and stock

### Prompt 39

Ok, now onto problem 6: Tools: product info and stock. I want to give the agent tool that look up real info from @hw4/data/campus_customs.db , specifically Product description, Price, and how many are in stock (and show by size when the customer asks). The agent HAS to use this database, it should not invent prices or quantities. If a size is out of stock it needs to say so clearly. Then help me expand @hw4/backend/prompts/prompt.md so the agent knows to call these tools for price and stock questions. Add or update return types in @hw4/backend/models.py

### Prompt 40

now, in output/harness.md, can you list each tool and explain which model fields I chose for lookup results and an explanation as to why. ask me questions if you need to know what i chose

### Prompt 41

yeah, lets add it. and yes, add those tools

### Prompt 42

In @hw4/output/harness.md , write it as my decision. and what I meant is include the 4 tools you mentioned earlier.

## Problem 7: Chat search that updates the page

### Prompt 43

Now onto Problem 7: Chat search that updates the page. When a customer asks about a type of item (ex. what t-shirts do you have) the agent should search the catalogue and the website should dynamically show those matching items as product cards (including image, name, price, and short info)

### Prompt 44

can you update @hw4/backend/prompts/prompt.md and @hw4/output/harness.md to show how search results reach the page for the feature we just added?

## Problem 8: Customer memory

### Prompt 45

onto problem 8: Customer memory. When a customer is logged in, I want to save their chat history in the database in an appropriate table. the table should reload when they return to the site. the agent should know WHO is chatting (name and email) - put this in agent deps and/or tools the agent can call. I also want to pass / build in page context. if someone is on a produt page and asks "do you have this in blue"? the agent should know which item they mean. put this code into the agent context. guests can still use the chat feature, but history only needs to be built in for logged-in users.

### Prompt 46

can you document in @hw4/output/harness.md how chat history is stored, what customer fields the agent sees, and how page context is passed? be a little detailed and make it soundl ike me

### Prompt 47

take out the "what I tested" from harness.md.

## Problem 9: Usability improvements

### Prompt 48

that's fine. onto problem 9: Usability improvements.

### Prompt 49

the first front end improvement I want to make is product photo backgrounds. I want all the product photos to have a white background so they show up as "floating" on the website. some products, like "Basic Hoodie Big Yale" have a black background. can you make this fix?

### Prompt 50

can you make sure the black background between the sleeves and the body of those items you just fixed, is cut out and turned white as well? For example, Baseball Left Chest Crewneck

### Prompt 51

Front-end usability upgrade #2: I also want to add Filters on the Product page, filter by Size, color, item type, and price. also add a sort function to sort by price, relevance, and alphabetical, for most to least for all

### Prompt 52

great, now backend usability improvement #1: I want to update password requirements (and update output/harness.md as well). I want a 5 time limit on login attempts, I also want password requirement to mean minimum 10 characters, both numbers and letters, with one special character.

### Prompt 53

also can you do this for frontend improvement #2: when the personal assistant dynamically loads matching product items, if filters are needed, i want the assistant to apply those. oh and also for backend improvement #1: if an existing user password doesn't meet these new requirements, i want to prompt the user to reset their password

### Prompt 54

What's another backend improvement you suggest making?

### Prompt 55

Let's do #2 - automated backend tests, for my second backend improvement

### Prompt 56

I want to stick to the original file layout though. can you make it so backend improvement #2 does not create any new files that don't fit the original file layout?

### Prompt 57

yeah, move those into tools.py

### Prompt 58

Write output/usability.md. In there, document all 4 usability improvemnts I made. make it sound like me. For each, clarify what I added and how it helps a potential shopper.

## Problem 10: Style the website

### Prompt 59

ok onto problem 10: Style the website. let's add some personality to the About Us page

### Prompt 60

Can you fix  this on the About Us page - it's hard to read
[Image attached: screenshot of the "Ask the assistant" button on the About Us page, white text on a light gray button]

### Prompt 61

Can we personalize the personal assistant - make it fun. Let's make it Bill Clinton themed! (just the assistant). be SUPER creative with it

### Prompt 62

make sure to frame bill clinton as a Yale alum. can we also add a picture of him popping out of the personal assistant window?

### Prompt 63

[Answer selected in response to my question about downloading the portrait]

- May I download this official White House portrait of Bill Clinton from Wikimedia Commons and use it for the 'popping out of the chat window' effect? → Yes, download it (Recommended)

### Prompt 64

[Image attached: screenshot of the chat window with the portrait circle sticking out above the window, face cut off]

Can you make it so his face is actually inside the window, not popping out of the window

### Prompt 65

Can you add an "Explore" Tab on the top sidebar? My vision for this tab is that it includes about 20 locations on/around Yale campus that are iconic, and recommends one item from the catalogue to wear to that location. It's just a fun, interactive tab. I want the recommended product to be clickable and go to that product page

### Prompt 66

I want all 20 locations in one single slideshow that people can click through. include one large hd image of each location

### Prompt 67

[Answer selected in response to my question about downloading the 20 location photos]

- May I download these 20 photos from Wikimedia Commons (about 141 MB of originals, resized to about 8 MB for the site) for the Explore slideshow? → Yes, download all 20 (Recommended)

### Prompt 68

let's just use the photos you have so far and scrap the rest

### Prompt 69

actually can you make this slideshow take up the leftmost 70% of the screen, and on the right have a map of the campus with pins of all the locations?

### Prompt 70

No, it's fine. At the bottom, can you give me credit "Isha Shah" for the website

### Prompt 71

can you standardize the fonts in the bottom bar?

### Prompt 72

Can you write output/design.md and document ALL stylistic changes / creative design changes I've made to the website under problem 10?

### Prompt 73

Can you list out all the earlier styling? I'll let you know if I want it added or not?

### Prompt 74

Can you include the points under Overall look and feel, Navigation bar, Home page, and Inner pages in @hw4/output/design.md ? Make it super succinct though

### Prompt 75

Can you make all of @hw4/output/design.md just 30% shorter?

## Problem 11: Site testing (app check)

### Prompt 76

Onto Problem 11: Site testing (app check). Create output/app_check.html. Make it a page I can double click open and edit

### Prompt 77

Wait don't pre-populate @hw4/output/app_check.html . I want to put content in myself and then have you format it later.

### Prompt 78

ok, done with the html. can you take the screenshots i've put in @hw4/output/app_check.html and move them into output/app_check_images and delete them from @hw4/output/app_check.html . then link them from @hw4/output/app_check.html with relative paths (ex. app_check_images/inventory.png)

### Prompt 79

wait what did i just edit? I thought i typed in content in the Files window into @hw4/output/app_check.html . did i put it somewhere else by accident just now?

### Prompt 80

Can you put this in output/app_check_images

(Attached: a screenshot of the Products page with the Quarter-Zips, M, and Blue filters applied.)

### Prompt 81

this one too

(Attached: a screenshot of the Products page after asking the assistant about hoodies in a small, with the Size S filter applied and the chat panel open.)

### Prompt 82

this one too

(Attached: a screenshot of the chat panel answering "what's the inventory level of basic hoodie big yale in size M?" with 5 in stock.)

### Prompt 83

can you store all 3 screenshots as the same file type - png?

### Prompt 84

what's the link to the website again

### Prompt 85

give me temrinal code to get to the front end folder

### Prompt 86

i want to make the HTML easy to grade by adding documentation into @hw4/output/app_check.html . Can you add 3 sections in there. The first test will be for "Chat checking the inventory level of an item to ensure honest stock and price from the database". For this one, link to @hw4/output/app_check_images/assistant_inventory.png with relative paths

### Prompt 87

To clarify, I don't need you to actually perform the test, just write the documentation I ask for. Wipe @hw4/output/app_check.html and start over. Include the heading, the relative path link to to @hw4/output/app_check_images/assistant_inventory.png , and 1-2 sentences on how the screenshot proves the test.

### Prompt 88

Do the same for Test #2: "The dynamic search-result cards appearing after a category question" and link to @hw4/output/app_check_images/assistant_size_filter.png

### Prompt 89

And the same for Test #3: "Adding filters and sort by functions to the Products page" and use @hw4/output/app_check_images/products_filters.png

### Prompt 90

For the 3 images, make sure you link them from @hw4/output/app_check.html with relative paths (ex. app_check_images/inventory.png). is this done right?

### Prompt 91

can you replace the @hw4/output/app_check_images/products_filters.png png with this one: and update @hw4/output/app_check.html accordingly

(Attached: a screenshot of the Products page with the Jackets filter on, showing 8 of 102 products sorted "Alphabetical: A to Z".)

### Prompt 92

now, how might a grader go about opening @hw4/output/app_check.html ?

### Prompt 93

don't change the content in @hw4/output/app_check.html but can you style it so it sort of matches my website?

### Prompt 94

put the problem # at the top of the page and label each test as #1, #2, #3. also can you make it so the screenshot appears on the right of the 1-2 sentence descriptions

### Prompt 95

Update this "The screenshot shows the Products page right after I asked the Personal Assistant about hoodies: the page now shows only hoodie product cards (23 of 27 products) under a banner saying the results were found by the Personal Assistant. The assistant's reply in the chat panel says those hoodies are showing on the page, which shows the cards appeared on the page because of the chat question." to also mention that the assistant auto-applied the relevant size filter for size small. Update this "The screenshot shows the Jackets item type checked ("Clear all (1)") and the grid narrowed from 102 products to the 8 jackets, so the filter panel is changing what the page shows. The "Sort by" menu is set to "Alphabetical: A to Z" and the cards run Benjamin Franklin, Berkeley, then Brooks Brothers, which shows the sort is putting the results in order." because the Clear all filter is not applied, I applied the Jackets filter and then sorted by alphabetical order

### Prompt 96

can you make the screenshots a bit bigger though so they are readable

### Prompt 97

revert the size of the first screenshot, otherwise all good

### Prompt 98

I do want it centered again.

## Problem 12: Audit trail, safety, and finish harness

### Prompt 99

Now onto Problem 12: Audit trail, safety, and finish harness. I want to make output/audit_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). I don't want it to wipe between runs, just append/add onto it.

### Prompt 100

Also, let's add some safety rules for the agent in @hw4/backend/prompts/prompt.md . Add rules for never exposing sensitive user data/info, never invent product/stock info, stay within the tools/capabilities i've given the agent, always protect the audit trail, limit tool usage - don't repeatedly call the tool if it is failing or returning the same info (help me quantify this one reasonably)

### Prompt 101

Yes, now let's finish @hw4/output/harness.md so it's clear to anyone looking how the system works. Can you especially include: 1) model fields in @hw4/backend/models.py and why I chose them, 2) tools and abilities, 3) safety rules I just added, and 4) specs (loop limits, result caps, models, how to run front and back end). ask me if you. have anny questions

### Prompt 102

anything you added that i did not particularly ask for but you thought was relevant?

### Prompt 103

let's just make @hw4/output/harness.md about 30% more concise

## Problem 13: Push to GitHub and submit the URL

### Prompt 104

Ok great, onto Problem 13: let's do README.md first, and in here let's explain how to run the front end and back end after placing the data pack. context for this is for submission, we need to push @hw4 to a public github repository. then, separately i will submit the repo URL so the graders cann open and clone the link. i will not be uploading a zip for this hw. as a reminder, i don't want to include my real .env, @hw4/data/campus_customs.db or product images in the Github repo. I want to use .gitignore and include .env.example with placeholders only. as a reminder, this is the expected file layout (see attached) and the agent itself is 4 files under backend/ : @hw4/backend/prompts/prompt.md , @hw4/backend/agent.py , @hw4/backend/tools.py and @hw4/backend/models.py

(Attached: a screenshot of the expected hw4/ file layout, plus the local-only data pack: data/campus_customs.db and data/products/.)

### Prompt 105

oh btw problem 13 is called Push to GitHub and submit the URL

### Prompt 106

OH btw, before we proceed, mI do want to run the agent once just to test @hw4/output/audit_trail.json

### Prompt 107

i asked the PA to show me hoodies in a size M

### Prompt 108

lert's keep the entries as proof that the trail works.

### Prompt 109

are we ready to push though - check one more time. i didn't see .env.example or .gitignore in the h4 folder

(Attached: the expected file layout screenshot again.)

### Prompt 110

and is there anything extra on the folder that shouldn't be there?

### Prompt 111

okay, walk me through how to submit this assignment now

### Prompt 112

on step 5: zsh: command not found: gh is what im seeing

### Prompt 113

isha@Ishas-MacBook-Air AI Class % gh repo create campus-customs-hw4 --public --source=. --remote=origin --push
current directory is not a git repository. Run `git init` to initialize it
isha@Ishas-MacBook-Air AI Class %

### Prompt 114

✓ Pushed commits to https://github.com/ishakshah/campus-customs-hw4.git

### Prompt 115

one more thing i want to fix - the colors filter doesn't seem to be working properly. can you make sure, for each product, you arae identifying one primary color per product only when filters are being applied on the products page?

### Prompt 116

what's the link to the website?

### Prompt 117

great, what's the terminal code to push just the changes to github?

### Prompt 118

did it work?
