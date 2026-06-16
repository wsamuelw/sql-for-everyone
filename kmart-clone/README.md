# Kmart Australia Clone

A clone of the Kmart Australia search results and product detail page, featuring real product images scraped from Kmart's CDN via Google Images.

## Project Structure

```
kmart-clone/
├── index.html          # Search results page (16 robot toy products)
├── product.html        # Product detail page (Daniel Wong the Robot Brother)
├── images/             # Product images downloaded from Kmart CDN
│   ├── intelligent-robot-smart.jpg    # Daniel Wong main image (child-robot hybrid)
│   ├── rc-police-robot.jpg
│   ├── intelligent-robot.jpg
│   ├── rc-octobot.jpg
│   ├── giant-transforming.jpg
│   ├── remote-control-dog.jpg
│   ├── buzz-lightyear.jpg
│   ├── optimus-prime.jpg
│   ├── dino-rc.jpg
│   ├── mechanical-robot.jpg
│   ├── tamagotchi-robot.jpg
│   ├── space-robot.jpg
│   ├── stem-robot-2.jpg
│   ├── stem-robot-3.jpg
│   └── stem-robot-4.jpg
└── README.md
```

## How to Run

No build step — it's static HTML. Just open `index.html` in a browser.

```bash
# Option 1: Double-click index.html

# Option 2: Local server
cd /Users/samuel/projects/kmart-clone
python3 -m http.server 8080
# Open http://localhost:8080

# Option 3: Quick open on macOS
open index.html
```

## How It Was Built

### 1. Initial Clone (emoji placeholders)
- Built a single-file `index.html` replicating Kmart's layout
- Used emoji placeholders for product images
- Features: header, search bar, category nav, filter sidebar, product grid, sort bar, pagination, footer

### 2. Image Scraping
Kmart's CDN (Akamai) blocks all automated access (403). Workaround:
- Searched Google Images for `site:kmart.com.au robot toy`
- Clicked each product thumbnail to expand
- Extracted `assets.kmart.com.au` image URLs from the expanded panel via JS
- Downloaded images directly from Kmart's CDN (CDN URLs aren't blocked, only the site itself)

```javascript
// Extract Kmart CDN image URL from expanded Google Images panel
document.querySelectorAll('img').forEach(img => {
  if (img.src.includes('assets.kmart.com.au') && img.naturalWidth > 100) {
    console.log(img.src); // Full-res product image
  }
});
```

### 3. Product Page
- Created `product.html` for Daniel Wong the Robot Brother
- Layout: image gallery, product info, quantity selector, add to cart, delivery info, tabs (Description/Specifications/Reviews)
- Linked from search page via `link` property in product data

## Key Design Details

- **Brand colours:** Red `#E60012`, dark `#1a1a1a`, grays for borders/text
- **Font:** Inter (Google Fonts)
- **Layout:** Max-width 1440px, 24px padding, CSS Grid for product cards (4-col → 3 → 2 responsive)
- **Sticky header** with search bar
- **Filter sidebar** with category, price range, brand, rating, availability
- **Product cards** with image, badge (New/Sale/Best Seller), wishlist heart, category, title, star rating, price (with was/save), Add to Cart button
- **Footer** with 4-column links, social icons, payment badges

## Customisation

### Change search term
In `index.html`, update:
- Search input `value="robot"` → your term
- Results title `Results for "<em>robot</em>"` → your term

### Add/edit products
In the `products` array in `index.html`:
```javascript
{
  name: "Product Name",
  category: "Category",
  price: 29.00,
  wasPrice: 39.00,    // null if no sale
  rating: 4.5,
  reviews: 128,
  badge: "sale",       // "sale" | "new" | "bestseller" | null
  img: "images/filename.jpg",
  link: "product.html" // null if no product page
}
```

### Change Daniel Wong's details
In `product.html`, update:
- Title, price, rating, review count in the HTML
- Description in the `<div class="description">` section
- Review content in the `<div class="review-card">` section

## Sharing Privately

**GitHub Pages (private repo):**
1. Create private repo on GitHub
2. Push this folder
3. Enable Pages in Settings → Pages → Source: main branch
4. Add collaborator in Settings → Collaborators
5. Collaborator must be logged in to GitHub to view

**ngrok (temporary):**
```bash
python3 -m http.server 8080 &
ngrok http 8080 --basic-auth="user:pass"
```

**Netlify Drop (public):**
Drag folder to https://app.netlify.com/drop — not private.

## Notes

- Images are from Kmart's CDN (`assets.kmart.com.au`). They may break if Kmart changes their URL structure.
- All prices, ratings, and reviews are fake/placeholder data.
- No backend — purely static HTML/CSS/JS.
- Responsive down to mobile (375px).
