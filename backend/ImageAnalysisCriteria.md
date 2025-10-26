# Image Analysis Criteria

This document describes the criteria used for analyzing advertisement images.

## Analysis Fields

### 1. product_visibility_score
How prominently the product appears in the image:
- **low**: Product is barely visible, small in the image, or only mentioned in text without clear visual presence
- **medium**: Product is visible but not the main focus (shares space with other elements, moderate size)
- **high**: Product dominates the image composition, is clearly the focal point, or takes up significant visual space with clear details

### 2. visual_density
Amount of visual clutter and negative space in the image:
- **low**: Image has lots of negative/empty space with minimal objects (minimalist, clean design)
- **medium**: Balanced mix of content and negative space
- **high**: Image is crowded with many objects, text, or visual elements with little negative space

Analyze based on:
- Portion of image occupied by negative space vs objects
- Number of visual elements on screen
- Amount of empty/breathing room in composition
- Text density
- Overall visual clutter

### 3. color_palette
Array of UP TO 5 hex color codes (format: #RRGGBB) representing the most recurring colors in the image.
- Analyze the image and identify up to 5 colors that appear most frequently
- Order from most to least recurring
- Use uppercase letters for hex codes
- Example: ["#FF5733", "#C70039", "#900C3F", "#581845", "#FFC300"]

### 4. age_demographic
Age range of the MAJORITY of people visible in the advertisement:
- **child**: Ages 0-12
- **teenage**: Ages 13-19
- **adult**: Ages 20-64
- **senior**: Ages 65+
- **N/A**: If there are no PROMINENT humans visible in the advertisement

### 5. gender_demographic
Gender representation of people visible in the advertisement:
- **male**: Predominantly male
- **female**: Predominantly female
- **other**: Other gender representation
- **N/A**: If there are NO PROMINENT humans visible in the ad

### 6. verbosity
Amount of text content in the image:
- **none**: No visible text or very minimal text
- **low**: Occasional text elements or brief text
- **medium**: Moderate amount of text throughout
- **high**: Image is heavily text-based with lots of on-screen text

### 7. visual_complexity
Compositional complexity of the image:
- **minimal**: Simple composition with few elements, clean lines, single focal point (like minimalist product shots)
- **moderate**: Balanced composition with multiple elements but clear hierarchy
- **complex**: Busy composition with many competing elements, layered imagery, or intricate details that require visual processing

### 8. purchase_urgency
How obvious and urgent the call-to-action is based on OCR text:
- **low**: Ad focuses on brand/product awareness with subtle or delayed messaging (product awareness only)
- **medium**: Clear product features or soft CTAs like 'learn more' or 'introducing the new...'
- **high**: Urgent, time-sensitive CTAs with phrases like 'limited time', 'buy now', 'X% off', 'for the next 3 days', or other immediate purchase signals

### 9. formality_level
Communication style based on OCR text and visual style:
- **1**: Meme speak - Internet slang, all caps, emojis, casual abbreviations
- **2**: Casual - Conversational, friendly, informal tone
- **3**: Semi-professional - Polished but approachable
- **4**: Professional - Formal, corporate, business language

### 10. benefit_framing
How benefits are presented based on OCR text:
- **outcome**: Focuses on results/benefits user will achieve ("Get fit", "Save money", "Feel confident")
- **feature**: Focuses on product attributes ("Made with X", "Features Y", "Includes Z")
- **social_proof**: Focuses on testimonials, reviews, popularity ("1M+ users", "5-star rated", "Trusted by...")

### 11. scene_setting
Brief description of the primary scene/location/setting shown in the image.
- Examples: "kitchen", "office", "park", "city street", "living room"

## Emotional Indices

All emotional indices are decimal numbers from 0.0 to 1.0, representing the presence and prominence of specific imagery themes. Use increments of 0.1 (e.g., 0.0, 0.1, 0.2, ..., 0.9, 1.0).

### 12. fear_index
Presence of fear/security-related imagery (0.0 = none, 1.0 = heavy presence):
- Locks, shields, security cameras, alarms
- Warnings, danger symbols, threats
- Protective gear, barricades
- Crime-related imagery, disaster imagery
- Surveillance equipment

### 13. comfort_index
Presence of comforting imagery (0.0 = none, 1.0 = heavy presence):
- Beds, blankets, pillows, cozy furniture
- Warm lighting (golden/soft lights)
- Fireplaces, hot beverages (coffee/tea)
- Soft textures, plush materials
- Relaxing environments, home settings
- Gentle colors, peaceful scenes

### 14. humor_index
Presence of comedic elements and intent (0.0 = none, 1.0 = heavy presence):
- Comedic timing and pacing
- Use of irony/sarcasm/satire
- Absurd or unexpected situations
- Visual gags or slapstick
- Witty dialogue or wordplay
- Parody or mockery of common tropes
- Exaggerated reactions or behaviors
- Comedic character archetypes
- Situational comedy or skits
- Meme references or internet humor

Evaluate whether the image appears to be intentionally trying to make viewers laugh or smile.

### 15. success_index
Presence of success/achievement imagery (0.0 = none, 1.0 = heavy presence):
- Awards, trophies, medals, podiums
- Celebrations, champagne, confetti
- Business suits, offices, boardrooms
- Graduation caps, diplomas, certificates
- Upward graphs, charts showing growth
- People cheering, high-fiving, fist-pumping
- Luxury items as symbols of success
- Victory poses, winning moments

### 16. love_index
Presence of love/romance imagery (0.0 = none, 1.0 = heavy presence):
- Couples holding hands, kissing, embracing
- Hearts, flowers, romantic dinners
- Wedding imagery, rings, proposals
- Intimate moments, gazing into eyes
- Romantic settings (sunset, beach, candlelight)
- Love letters, valentine's imagery
- Romantic gestures, date nights

### 17. family_index
Presence of family/belonging imagery (0.0 = none, 1.0 = heavy presence):
- Multi-generational gatherings
- Parents with children
- Family meals, holiday gatherings
- Group hugs, family activities
- Home/household scenes with multiple people
- Birthday parties, family celebrations
- Sibling interactions, grandparents
- Family photos, domestic harmony

### 18. adventure_index
Presence of adventure/freedom imagery (0.0 = none, 1.0 = heavy presence):
- Open roads, mountains, horizons
- Travel imagery, planes, exotic locations
- Outdoor activities, extreme sports
- Breaking free imagery, birds flying
- Exploration, discovery themes
- Wind in hair, arms spread wide
- Backpacks, camping, hiking, sailing
- Motorcycles, off-road vehicles

### 19. nostalgia_index
Presence of nostalgic imagery (0.0 = none, 1.0 = heavy presence):
- Vintage filters, sepia tones
- Old photos, memories, flashbacks
- Retro products, classic cars
- Childhood toys, games
- 'Good old days' imagery
- Historical references, throwback styles
- Old music, vintage clothing
- Antiques, old technology
- Childhood memories, school days imagery

### 20. health_index
Presence of health/vitality imagery (0.0 = none, 1.0 = heavy presence):
- Exercise, running, yoga
- Fresh fruits, vegetables, water
- Medical imagery (positive context)
- Energy, jumping, active movement
- Sunrise, morning routines
- Clean, bright, airy spaces
- Athletic performance
- Vitamins, supplements, healthy cooking
- Fitness equipment, sports activities

### 21. luxury_index
Presence of luxury/exclusivity imagery (0.0 = none, 1.0 = heavy presence):
- Gold, silver, jewels, expensive materials
- High-end brands, designer items
- VIP areas, exclusive access
- Elegant settings, fine dining
- Premium packaging, limited editions
- Sophisticated color palettes (black, gold, deep colors)
- Luxury cars, yachts, private jets
- Mansions, designer fashion, expensive watches