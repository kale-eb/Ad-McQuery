# Video Analysis Criteria

This document describes the criteria used for analyzing video advertisements.

## Analysis Fields

### 1. main_product
Identify the exact product, service, or event being promoted in the advertisement.
- Be specific (e.g., 'iPhone 15 Pro', 'Netflix subscription service', 'Coca-Cola Classic', 'Toyota Camry 2024', 'McDonald's Big Mac', 'Black Friday Sale Event')
- This should be the primary thing the advertiser wants viewers to purchase, subscribe to, or engage with

### 2. targeting_type
Whether the ad assumes prior brand familiarity:
- **first_impression**: Introducing brand/product to new audience
- **retargeting**: Assumes familiarity with brand/product

### 3. verbosity
Amount of text and spoken content in the video:
- **none**: No visible text or spoken dialogue (just music/sound effects)
- **low**: Occasional text elements or brief dialogue moments
- **medium**: Moderate amounts of text or speaking throughout
- **high**: Heavily text-based or dialogue-heavy with lots of talking or on-screen text

### 4. target_age_range
Age range of the actual PURCHASER/BUYER, not the end user of the product.
- Consider who has the purchasing power and decision-making authority
- Examples:
  - Kids' clothing targets parents (adults), not children
  - Senior medication may target middle-aged children buying for parents
  - Toys may target children only if messaging is playful/colorful to encourage nagging, otherwise targets parents
- Focus on who will actually make the purchase decision and pay for the product
- Format: Specific age range like 18-25, 25-35, 35-50, 50+

### 5. target_income_level
Inferred income level of target audience:
- Infer from product type, pricing cues, lifestyle depicted
- Format: Specific income level description

### 6. target_geographic_area
Geographic targeting of the advertisement:
- Infer from product, explicit mentions, setting, cultural references
- Format: Specific geographic type (e.g., 'X county', 'East Coast US', 'Urban areas')

### 7. target_interests
Hobbies and interests the target customer would likely have:
- Array of up to 3 customer interests
- Example: ["fitness", "cooking", "travel"]

### 8. hook_rating
Rating of how engaging the first 3-5 seconds are (1-5 scale):
- **1**: Boring/generic start that viewers could easily scroll past
- **2**: Mildly interesting but not compelling
- **3**: Moderately engaging with some interesting elements
- **4**: Very captivating with strong attention-grabbing elements
- **5**: EXTREMELY captivating with instant attention-grabbers like loud sound effects, shocking visuals, crazy facts/statements, or visually stunning moments that would stop scrolling immediately

Important: A 5 must have something genuinely surprising or captivating that happens instantly. Product relevance is irrelevant - focus purely on attention-grabbing power.

### 9. purchase_urgency
How obvious and urgent the call-to-action is:
- **low**: Focuses on brand/product awareness with subtle or delayed product reveal (product shown only at the end)
- **medium**: Clear product features or soft CTAs like 'learn more' or 'introducing the new...'
- **high**: Urgent, time-sensitive CTAs with phrases like 'limited time', 'buy now', 'X% off', 'for the next 3 days', or other immediate purchase signals

### 10. message_types
List all applicable message types (can be multiple):
- **humor**: Uses comedy/jokes to be memorable
- **storytelling**: Creates narrative/mini-story for emotional connection
- **demonstration**: Shows product in action/how it works
- **emotional_appeal**: Tugs at heartstrings using feelings like nostalgia/fear/joy
- **problem_solution**: Identifies pain point then presents product as solution

Format: Array of applicable types, e.g., ["humor", "demonstration"]

### 11. product_visibility_score
How prominently the product appears throughout the video:
- **low**: Product is barely shown or only mentioned briefly
- **medium**: Product appears multiple times or has moderate screen time
- **high**: Product is prominently featured throughout the ad with clear close-ups or demonstrations

### 12. visual_density
Amount of visual clutter and negative space:
- **low**: Screen has lots of negative/empty space with minimal objects (minimalist, clean design)
- **medium**: Balanced mix of content and negative space
- **high**: Screen is crowded with many objects, text, or visual elements with little negative space

Analyze based on:
- Portion of screen occupied by negative space vs objects
- Number of visual elements on screen
- Amount of empty/breathing room in composition
- Text density
- Overall visual clutter

### 13. color_palette
Array of UP TO 5 hex color codes (format: #RRGGBB) representing the most recurring colors in the video.
- Analyze the video frames and identify up to 5 colors that appear most frequently throughout the media
- Order from most to least recurring
- Use uppercase letters for hex codes
- Example: ["#FF5733", "#C70039", "#900C3F", "#581845", "#FFC300"]

### 14. age_demographic
Age range of the MAJORITY of people visible in the advertisement:
- **child**: Ages 0-12
- **teenage**: Ages 13-19
- **adult**: Ages 20-64
- **senior**: Ages 65+
- **N/A**: If there are no PROMINENT humans visible in the advertisement

### 15. gender_demographic
Gender representation of people visible in the advertisement:
- **male**: Predominantly male
- **female**: Predominantly female
- **other**: Other gender representation
- **N/A**: If there are NO PROMINENT humans visible in the ad

### 16. activity_level
Visual dynamism and editing pace:
- **sedentary**: Video has few cuts and camera angle changes (slow-paced, static shots, long takes)
- **dynamic**: Video has frequent cuts and camera angle changes (fast-paced editing, quick scene transitions, multiple perspectives)
- **N/A**: If there are no humans visible in the video

Analyze the editing rhythm and camera movement throughout the video.

### 17. music_intensity
Analysis of background music or soundtrack:
- **low**: Music is soft, slow-tempo, ambient/calm genres (e.g., acoustic, classical, soft background music)
- **medium**: Music has moderate tempo and volume with balanced energy (e.g., pop, indie, moderate beats)
- **high**: Music is loud, fast-tempo, energetic genres (e.g., rock, EDM, hip-hop, intense orchestral)

If there is no music, default to "low".

Analyze based on tempo, loudness, and genre.

### 18. scene_cuts
Array of timestamps (in seconds) indicating when SIGNIFICANT visual cuts or scene changes occur in the video.

Include:
- Location/setting changes
- Major camera angle changes
- Significant zoom ins/outs
- Different angles of the same scene

Format: Array of decimal numbers, e.g., [0.5, 2.3, 5.1, 8.7]

### 19. visual_motifs
Prominent visual elements or items that appear repeatedly throughout the video, excluding the main product itself.

Focus on:
- Design elements, symbols, colors, shapes, or objects that create visual consistency or thematic reinforcement
- Examples: ['golden sparkles', 'red checkmarks', 'flowing water', 'geometric patterns', 'vintage frames', 'neon lighting', 'hand gestures']

Format:
- Array of 3-5 most prominent motifs
- List only elements that appear multiple times and contribute to the visual identity or messaging
- Use "N/A" if none

### 20. scene_settings
Array of general location types or settings where the video was filmed.

Focus on:
- Broad filming locations rather than specific scene descriptions
- Examples: ['modern kitchen', 'urban office', 'mountainous prairie', 'suburban backyard', 'beach coastline', 'city street', 'rural farmland', 'indoor studio']

Format:
- If multiple distinct locations are used, include all of them
- Keep descriptions concise and location-focused

## Emotional Indices

All emotional indices are decimal numbers from 0.0 to 1.0, representing the presence and prominence of specific imagery themes. Use increments of 0.1 (e.g., 0.0, 0.1, 0.2, ..., 0.9, 1.0).

### 21. fear_index
Presence of fear/security-related imagery (0.0 = none, 1.0 = heavy presence):
- Locks, shields, security cameras, alarms
- Warnings, danger symbols, threats
- Protective gear, barricades
- Crime-related imagery, disaster imagery
- Surveillance equipment

### 22. comfort_index
Presence of comforting imagery (0.0 = none, 1.0 = heavy presence):
- Beds, blankets, pillows, cozy furniture
- Warm lighting (golden/soft lights)
- Fireplaces, hot beverages (coffee/tea)
- Soft textures, plush materials
- Relaxing environments, home settings
- Gentle colors, peaceful scenes

### 23. humor_index
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

Evaluate whether the video appears to be intentionally trying to make viewers laugh or smile.

### 24. success_index
Presence of success/achievement imagery (0.0 = none, 1.0 = heavy presence):
- Awards, trophies, medals, podiums
- Celebrations, champagne, confetti
- Business suits, offices, boardrooms
- Graduation caps, diplomas, certificates
- Upward graphs, charts showing growth
- People cheering, high-fiving, fist-pumping
- Luxury items as symbols of success
- Victory poses, winning moments

### 25. love_index
Presence of love/romance imagery (0.0 = none, 1.0 = heavy presence):
- Couples holding hands, kissing, embracing
- Hearts, flowers, romantic dinners
- Wedding imagery, rings, proposals
- Intimate moments, gazing into eyes
- Romantic settings (sunset, beach, candlelight)
- Love letters, valentine's imagery
- Romantic gestures, date nights

### 26. family_index
Presence of family/belonging imagery (0.0 = none, 1.0 = heavy presence):
- Multi-generational gatherings
- Parents with children
- Family meals, holiday gatherings
- Group hugs, family activities
- Home/household scenes with multiple people
- Birthday parties, family celebrations
- Sibling interactions, grandparents
- Family photos, domestic harmony

### 27. adventure_index
Presence of adventure/freedom imagery (0.0 = none, 1.0 = heavy presence):
- Open roads, mountains, horizons
- Travel imagery, planes, exotic locations
- Outdoor activities, extreme sports
- Breaking free imagery, birds flying
- Exploration, discovery themes
- Wind in hair, arms spread wide
- Backpacks, camping, hiking, sailing
- Motorcycles, off-road vehicles

### 28. nostalgia_index
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

### 29. health_index
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

### 30. luxury_index
Presence of luxury/exclusivity imagery (0.0 = none, 1.0 = heavy presence):
- Gold, silver, jewels, expensive materials
- High-end brands, designer items
- VIP areas, exclusive access
- Elegant settings, fine dining
- Premium packaging, limited editions
- Sophisticated color palettes (black, gold, deep colors)
- Luxury cars, yachts, private jets
- Mansions, designer fashion, expensive watches