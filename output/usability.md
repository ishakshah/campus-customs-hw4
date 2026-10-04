# Usability Improvements

After the first version of Campus Customs worked, I made four improvements to make it nicer to use. Two are on the front end (what shoppers see) and two are on the back end (what keeps the site safe and dependable). For each one, here's what I added and how it helps someone shopping on the site.

| # | Improvement | Where | Who it helps most |
|---|---|---|---|
| 1 | White product photo backgrounds | Front end | Anyone browsing products |
| 2 | Filters and sorting on the Products page, applied by the assistant too | Front end | Anyone looking for a specific item |
| 3 | Stronger passwords, a login attempt limit, and a prompt to update old passwords | Back end | Anyone with an account |
| 4 | Automated backend tests | Back end | Everyone, indirectly |

## 1. White product photo backgrounds (front end)

### What I added

Many of the product photos had black in them. Some had black bars down the sides, and 46 of the 102 had a completely black background, because a see-through background got turned into black when the photo was saved. About 26 others had a faint gray background (a 250 instead of a true 255 white). On a white website, they looked like dark boxes.

I fixed it on the backend, in the part that serves the photos, so the original files are never touched:

- Black bars are cropped off, and the photo is centered back into a square.
- A black background is turned white.
- The black gaps between the sleeves and the body (like on the Baseball Left Chest Crewneck) are cut out and turned white too.
- A faint gray background is turned into pure white.
- The edge around each garment is cleaned up, so there's no dark outline or speckles.
- Every photo link now carries a version number, so a shopper's browser fetches the new photo instead of showing an old cached copy.

I only cut out black that is truly pure black and wide enough to be a real gap. Dark navy shading and black details on a garment are left alone, so the clothes still look right.

### How it helps a shopper

Every garment now looks like it's floating on the page, with the same clean white look from one product to the next. Shoppers can compare items side by side without being distracted by black boxes, and the shop looks more polished and trustworthy. The products are the focus, not the photo editing.

## 2. Filters and sorting on the Products page (front end)

### What I added

The Products page has 102 items, so I added a filter panel and a sort menu:

- **Item type:** Hoodies, Sweatshirts, T-Shirts, Quarter-Zips, Jackets, and Long-Sleeve Performance Shirts.
- **Size:** XS to XXL. This only shows items that are actually in stock in the size you pick.
- **Color:** 11 color families, each with a small color swatch (Navy, Gray, White, Red, and so on). The catalogue has 22 different color names, so I grouped them to keep the list short.
- **Price:** a minimum and a maximum box.
- **Counts and clearing:** every option shows how many products it would give you, with your other filters taken into account. A **Clear all** button resets everything, and if nothing matches, the page says so and offers a way back.
- **Sorting:** relevance, price, and alphabetical, each in both directions (most to least, least to most; high to low, low to high; A to Z, Z to A).
- **On a phone:** the filters sit behind a **Filters** button so they don't take up the screen, and the products show two to a row.

I also made the Personal Assistant use the filters. If a shopper asks, "Show me navy hoodies in medium under $60," the assistant opens the Products page with Navy, size M, and a $60 maximum already switched on, and a banner says what it did. If they ask for "quarter-zips, cheapest first," it sets the sort too. The shopper can still change or clear any filter, so they stay in control.

### How it helps a shopper

Finding the right item in 102 products without filters means a lot of scrolling. Now a shopper can narrow things down in a few clicks: the type of item, their size, a color they like, and their budget. Because the size filter only shows what's in stock, they don't fall for something that's sold out in their size. The counts show what each filter will do before they click it. Someone who doesn't want to click through filters can just tell the assistant what they want, and the page sets itself up for them.

## 3. Stronger passwords, a login attempt limit, and a prompt to update old passwords (back end)

### What I added

Accounts hold a shopper's name, email, and saved chats, so I tightened the rules around passwords:

- **Stronger new passwords.** A password has to be at least 10 characters and include a letter, a number, and a special character. On the Create Account page, a checklist ticks off each rule as the shopper types. If something is missing, the error says exactly what, instead of just "invalid password."
- **A limit on login attempts.** After 5 wrong passwords, an account is locked for 15 minutes. Each wrong try says how many attempts are left, and the last one says how long to wait. It works the same way for emails that don't have an account, so the limit can't be used to find out who is registered, and a good login resets the count.
- **A prompt for old, weak passwords.** Passwords are stored in a scrambled form, so I can't read an old one later. But at the moment someone logs in, the server can check the password they typed. If it doesn't meet the new rules, they're sent to an "Update your password" page that explains why, and a banner reminds them across the site until they change it. They can choose "Not now," and they'll be asked again next time. Changing the password needs the current one, and wrong tries count toward the same 5-attempt limit.

### How it helps a shopper

It keeps their account and personal details harder to break into. Someone can't just sit there and keep guessing a shopper's password, and people with older, weaker passwords get a clear, friendly nudge to make them stronger. The live checklist and the "attempts left" messages mean the rules protect people without being confusing or frustrating.

## 4. Automated backend tests (back end)

### What I added

I wrote an automated test suite for the backend: 187 tests that run in about 13 seconds. They don't use my real database or my AI key. They use a small made-up catalogue and a scripted fake model, so they can run anywhere. They check things like:

- The password rules, the 5-attempt limit and its 15-minute timing, and the password update flow.
- The exact prices, stock counts, and sold-out sizes the assistant is allowed to use, and the check that stops it from quoting a price or quantity the database didn't give it.
- The filters the assistant switches on, and the item, size, and color grouping.
- Privacy: chat history only shows up for the person it belongs to, and a shopper's email isn't put in the assistant's instructions.
- The photo cleanup, including the gaps between sleeves and body.

To make sure the tests actually work, I broke the code on purpose in 12 different ways, like loosening the password rule or turning off the number check. Every one of those mistakes is now caught. (One got past at first, so I added a test for it.) The tests stay on my computer and aren't part of the submitted files, to keep the project layout exactly as required.

### How it helps a shopper

Shoppers never see the tests, but they feel the result. The prices and stock numbers they see are checked. The assistant can't invent a discount or a quantity, and their chats stay private. When I change something, like a filter or a password rule, the tests tell me right away if I broke something that already worked, so the site stays reliable.
