# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The scoring recipe weights genre (+2.0) twice as heavily as mood (+1.0), so it systematically favors users whose stated genre exists in the 18-song catalog over users whose mood or vibe is the stronger signal. Testing an adversarial profile (`genre=metal, mood=sad, energy=0.9`) showed the system will confidently rank a high-energy, wrong-mood song above the one song that actually matches the user's stated mood, purely because genre points outweigh a mood-plus-energy combination. The system also has no way to flag an internally contradictory profile ("sad" with a 0.9 energy target); it just scores whatever it's given and returns a ranked list with no warning. Genres and moods not well represented in the 18-song catalog (there's one song per genre in several cases) will get thin, low-confidence recommendations even when a real match doesn't exist. Because this is content-based only, a user's actual taste, likes, skips, replays, is invisible to the system; it can only ever match the profile it's told, so it will happily reinforce whatever genre/mood the user already typed in rather than surfacing something outside that box.

---

## 7. Evaluation  

Tested four profiles against the 18-song catalog (full terminal output in the README's [Experiments You Tried](README.md#experiments-you-tried) section): **High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`), **Chill Lofi** (`genre=lofi, mood=chill, energy=0.3`), **Deep Intense Rock** (`genre=rock, mood=intense, energy=0.9`), and an **adversarial** profile (`genre=metal, mood=sad, energy=0.9`) chosen specifically to contradict itself.

For each of the first three, I checked whether the top result matched my own intuition for that vibe. It did in all three cases: `Sunrise City` for pop/happy, `Library Rain` for lofi/chill, `Storm Runner` for rock/intense. Comparing High-Energy Pop and Chill Lofi shows what the system is actually testing for: the high-energy profile pulls upbeat, danceable tracks (`Sunrise City`, `Gym Hero`) while the low-energy profile pulls the opposite corner of the catalog (`Library Rain`, `Midnight Coding`), same scoring recipe, opposite result, because `energy` is the one numeric axis in the recipe and it's doing real work.

What surprised me was the adversarial profile: I expected the contradiction (metal/high-energy paired with mood "sad") to produce a messy or clearly-wrong top result, and it did, but not in the way I expected. `Iron Collapse` (aggressive metal) beat `Tears in Neon` (the only song actually tagged "sad") because 2.0 genre points plus a near-perfect energy match outscored the mood match. The system never notices the profile is self-contradictory; it just picks the highest scorer and moves on. I ran a follow-up weight-shift experiment (genre 2.0 to 1.0, energy points doubled) on this same adversarial profile and the result got worse, not better: `Tears in Neon` fell out of the top 5 entirely, replaced by songs matching nothing but raw energy. That confirmed the 2:1 genre-to-mood weighting, while it does over-favor genre, is doing more good than harm compared to the alternative I tried.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
