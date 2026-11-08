"""
AiJaga — retro "AiJaga TV" health assistant with Dr. Azmi (all-in-one Streamlit app).

Run it with:
    pip install --upgrade streamlit
    streamlit run aijaga_app.py

Optional (for AI chat answers): create .streamlit/secrets.toml with
    AGNES_API_KEY = "your-key"
Without a key, Dr. Azmi answers from the built-in AiJaga topic library.

Pages
    HOME          Dr. Azmi greeting + chat, big VIDEO and QUIZ buttons
    QUIZ          pick a field -> pick a topic -> 3 questions -> result (progress + XP saved for the session)
    VIDEO         pick a field -> pick a video -> watch (YouTube) + playlist + "Take the quiz"
Every page has a HOME button and the BRIGHT / DARK theme switch.
"""

import html
import json
import random
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide", initial_sidebar_state="collapsed")

DOCTOR = "Dr. Azmi"
Q_PER = 3  # questions per quiz

# ---------------------------------------------------------------------------
# 1. Colours (Bright and Dark themes)
# ---------------------------------------------------------------------------
THEMES = {
    "bright": {
        "page": "#F6F1E7", "frame": "#EBC99D", "frame_edge": "#D4A774", "frame_text": "#6E4F2C",
        "screen": "#E1EEEA", "scan": "rgba(255,255,255,0.5)", "ink": "#1C2B33", "sub": "#344A50",
        "card": "#FFFFFF", "chat_bg": "#F2F7F5", "teal": "#2D6A5C", "coral": "#E36F52",
        "chip": "#D3EAE2", "btn_text": "#FFFFFF", "online": "#2FAE5E",
        "ok": "#2F9E6B", "bad": "#D64545", "done_bg": "#DCDEDD", "done_ink": "#6A7378", "done_line": "#9AA3A8",
    },
    "dark": {
        "page": "#111517", "frame": "#3B3229", "frame_edge": "#2A231C", "frame_text": "#C9A982",
        "screen": "#13221F", "scan": "rgba(0,0,0,0.28)", "ink": "#E4F1ED", "sub": "#A8C3BC",
        "card": "#1A2E2A", "chat_bg": "#152623", "teal": "#5CC0A6", "coral": "#F08A6E",
        "chip": "#1F3A34", "btn_text": "#0D1916", "online": "#4FD481",
        "ok": "#2F9E6B", "bad": "#D64545", "done_bg": "#26323A", "done_ink": "#7D8B93", "done_line": "#4A5861",
    },
}


# ---------------------------------------------------------------------------
# 2. Quiz data
#    Q(question, correct_answer, wrong_1, wrong_2, wrong_3)
#    Answer order is shuffled every time a quiz starts.
# ---------------------------------------------------------------------------
def Q(question, correct, *wrong):
    return {"q": question, "answer": correct, "options": [correct, *wrong]}


FIELDS = [
    # ------------------------------------------------------------------ 0
    {
        "name": "Body Systems & Organs",
        "quizzes": [
            {"title": "Immune System", "questions": [
                Q("What best describes the main function of the immune system?", "To protect the body by identifying and defending against harmful foreign substances",
                  "To regulate the body's temperature and maintain internal balance", "To transport oxygen and nutrients to different parts of the body", "To remove waste products and regulate the body's fluid levels"),
                Q("What is the primary role of white blood cells (leukocytes) in the immune system?", "To identify and fight against harmful microorganisms that enter the body",
                  "To transport antibodies throughout the bloodstream", "To repair damaged tissues by producing new skin cells", "To carry oxygen to infected areas to support tissue recovery"),
                Q("How do antibodies help the immune system defend the body against harmful invaders?",
                  "They recognise and attach to specific antigens on foreign substances.",
                  "They break down damaged tissues to prevent infections from spreading", "They transport white blood cells towards areas affected by infections", "They create physical barriers that prevent microorganisms from entering the body"),
            ]},
            {"title": "Digestive System", "questions": [
                Q("What is the main function of the digestive system?", "To break down food so the body can absorb nutrients",
                  "To transport oxygen and nutrients through the bloodstream", "To remove excess water and waste from the blood", "To control how the body responds to its surroundings"),
                Q("What happens to food when it reaches the stomach?", "It is mixed with digestive juices and broken down further",
                  "It is absorbed directly into the bloodstream without further digestion", "It is converted into energy that the muscles can use immediately", "It is separated into oxygen and carbon dioxide"),
                Q("Where does most nutrient absorption take place?", "Small intestine",
                  "Large intestine", "Stomach", "Pancreas"),
            ]},
            {"title": "Gut", "questions": [
                Q("What are gut bacteria mainly responsible for?",
                  "Helping digest certain foods and supporting gut health",
                  "Producing oxygen for the body's cells", "Controlling the movement of muscles throughout the body", "Filtering harmful substances directly from the blood"),
                Q("Why is having a balance of good bacteria in the gut important?", "It helps maintain digestion and supports the body's natural defences",
                  "It allows the stomach to produce more acid for every type of food", "It prevents the body from absorbing too many nutrients", "It helps the kidneys remove waste more efficiently"),
                Q("Which of the following foods can help support healthy gut bacteria?",
                  "Yoghurt containing live cultures",
                  "Cheese made using fermented milk", "Whole-grain bread rich in dietary fibre", "Fresh fruit containing natural sugars"),
            ]},
            {"title": "Liver Function", "questions": [
                Q("What is one of the liver's main functions?", "Filtering blood and removing toxins",
                  "Regulating blood sugar levels by producing insulin", "Filtering excess water and salts from the bloodstream", "Producing digestive enzymes that break down proteins"),
                Q("What substance does the liver produce to help digest fats?", "Bile",
                  "Insulin", "Gastric juice", "Pancreatic enzymes"),
                Q("How does the liver help the body store energy?",
                  "By storing excess glucose as glycogen",
                  "By converting excess glucose directly into proteins", "By storing fatty acids for immediate use by muscles", "By breaking down glycogen into glucose for long-term storage"),
            ]},
            {"title": "Respiratory System", "questions": [
                Q("What is the main function of the respiratory system?",
                  "To take in oxygen and remove carbon dioxide from the body",
                  "To regulate blood pH by controlling the amount of bicarbonate", "To transport oxygen and nutrients to different body tissues", "To control the exchange of nutrients between blood and organs"),
                Q("What happens when you inhale?", "Air enters the lungs, bringing oxygen into the body",
                  "The diaphragm relaxes and moves upward, allowing the lungs to expand", "The chest cavity becomes smaller, pushing air into the lungs", "The lungs release carbon dioxide while taking in less oxygen"),
                Q("Where does the exchange of oxygen and carbon dioxide take place in the lungs?", "Alveoli",
                  "Bronchi", "Trachea", "Pleura"),
            ]},
            {"title": "Urinary System", "questions": [
                Q("What is the main function of the urinary system?",
                  "To filter blood and remove waste through urine",
                  "To regulate blood sugar and maintain energy balance", "To control the production of digestive fluids", "To transport oxygen and nutrients through the bloodstream"),
                Q("Which organs filter the blood to produce urine?", "Kidneys",
                  "Bladder", "Ureters", "Adrenal glands"),
                Q("What is the main function of the urinary bladder?", "To store urine until it is released from the body",
                  "To regulate the concentration of urine before it leaves the body", "To filter waste products and excess water from the blood", "To transport urine from the kidneys to the outside of the body"),
            ]},
            {"title": "Brain", "questions": [
                Q("What is the main function of the brain?", "To control and coordinate the body's activities, thoughts and movements.",
                  "To transport oxygen and nutrients to different organs", "To filter waste products from the blood", "To produce hormones that regulate digestion"),
                Q("Which part of the brain is mainly responsible for thinking, memory and learning?", "Cerebrum",
                  "Cerebellum", "Brain stem", "Spinal cord"),
                Q("Which part of the brain helps control balance and coordination?",
                  "Cerebellum",
                  "Cerebrum", "Brain stem", "Spinal cord"),
            ]},
            {"title": "Hormones", "questions": [
                Q("What are hormones?", "Chemical messengers that help control different body functions",
                  "Special proteins that transport oxygen through the blood", "Digestive substances that break food into smaller nutrients", "Cells that protect the body against harmful microorganisms"),
                Q("Which gland produces insulin to help regulate blood sugar levels?", "Pancreas",
                  "Thyroid", "Adrenal glands", "Pituitary gland"),
                Q("Which hormone is mainly responsible for the development of male secondary sexual characteristics?", "Testosterone",
                  "Estrogen", "Progesterone", "Cortisol"),
            ]},
            {"title": "Body Parts", "questions": [
                Q("Which body part do we use to see?", "Eyes", "Ears", "Nose", "Hands"),
                Q("Which body part pumps blood around the body?", "Heart",
                  "Stomach", "Lungs", "Brain"),
                Q("Which body part helps us maintain balance while walking and moving?", "Inner ear", "Knees", "Shoulder joints", "Rib cage"),
            ]},
            {"title": "Muscles", "questions": [
                Q("What happens to muscles when we exercise or lift weights?", "Muscle fibres experience small amounts of damage that the body repairs",
                  "Muscle fibres immediately increase in number during exercise", "Muscles become stronger because they store more oxygen", "Muscle tissues are replaced by fat during recovery"),
                Q("What helps muscles grow and recover after exercise?", "Proper nutrition and sufficient rest",
                  "Exercising continuously without taking breaks", "Reducing food intake to prevent muscle fatigue", "Avoiding movement until the muscles completely recover"),
                Q("How does the brain help muscles move?", "It sends signals through nerves that tell muscles when to contract",
                  "It produces energy directly inside muscle fibres", "It sends oxygen through the bloodstream to activate muscles", "It controls muscle movement by producing digestive enzymes"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 1
    {
        "name": "Nutrition & Healthy Habits",
        "quizzes": [
            {"title": "Drink Water", "questions": [
                Q("Why is water important for the human body?", "It helps regulate body temperature and supports normal body functions", "It provides the body with most of its daily energy", "It helps produce hormones that control growth", "It supplies oxygen directly to the body's organs"),
                Q("What can happen when the body does not get enough water?",
                  "Causes dehydration and can lead to various health issues",
                  "The body produces more red blood cells to replace lost fluids", "The digestive system begins absorbing nutrients more quickly", "The kidneys increase urine production to remove excess waste"),
                Q("Which part of the brain helps regulate thirst?",
                  "Hypothalamus",
                  "Cerebellum", "Brainstem", "Cerebral cortex"),
            ]},
            {"title": "Food Pyramid", "questions": [
                Q("What is the main purpose of a food pyramid?", "To guide people in choosing a balanced diet with appropriate food portions",
                  "To show which foods contain the highest number of calories", "To rank foods according to how quickly the body digests them", "To identify which foods should be completely removed from daily meals"),
                Q("Which food group is an important source of vitamins, minerals and dietary fibre?", "Fruits and vegetables",
                  "Meat and poultry", "Oils and fats", "Dairy products"),
                Q("Why should foods high in sugar, salt and unhealthy fats be consumed in limited amounts?",
                  "Excessive intake can increase the risk of health problems over time", "These foods prevent the body from absorbing all types of nutrients", "They cause the digestive system to stop breaking down carbohydrates", "They cause the digestive system to stop breaking down carbohydrates"),
            ]},
            {"title": "Urine Color", "questions": [
                Q("What does pale yellow urine generally indicate?", "The body is reasonably well hydrated",
                  "The kidneys are producing more waste than usual", "The body is losing too many minerals through sweating", "The bladder is storing urine for longer than normal"),
                Q("What can dark yellow urine indicate?", "The body may not be getting enough fluids",
                  "The kidneys are removing excess protein from the blood", "The body is producing more red blood cells", "The bladder is releasing urine at a faster rate"),
                Q("What should you do if your urine appears red or pink without an obvious dietary explanation?",
                  "Seek medical advice because it may indicate blood in the urine",
                  "Increase salt intake to restore the body's mineral balance", "Reduce water intake to prevent further changes in urine colour", "Wait several weeks because unusual urine colours are usually harmless"),
            ]},
            {"title": "Constipation", "questions": [
                Q("What is constipation?",
                  "Having difficulty passing stool or passing it less often than usual",
                  "A condition where food moves too quickly through the digestive system", "A condition where the stomach produces too much digestive acid", "When the intestines absorb nutrients more slowly than usual"),
                Q("Which of the following can help prevent constipation?",
                  "Eating fibre-rich foods, drinking enough water and staying physically active",
                  "Reducing fruit and vegetable intake while increasing protein consumption", "Avoiding physical activity to reduce pressure on the digestive system", "Limiting fluid intake to reduce the amount of waste produced"),
                Q("Why can a lack of dietary fibre contribute to constipation?",
                  "It makes the stool harder and more difficult to pass",
                  "It causes the stomach to produce less digestive acid", "It prevents the small intestine from absorbing water", "It increases the amount of fat stored around the intestines"),
            ]},
            {"title": "Holding Urine", "questions": [
                Q("What happens when you hold your urine for a long time?",
                  "Urine continues to collect in the bladder, causing it to stretch",
                  "The kidneys temporarily stop filtering waste from the blood", "The bladder begins breaking down waste substances in the urine", "The body redirects urine back into the bloodstream for storage"),
                Q("What may happen if someone frequently ignores the urge to urinate?", "It may contribute to bladder problems and increase the risk of urinary complications",
                  "It improves the bladder's ability to store larger amounts of urine permanently", "It causes the kidneys to produce less concentrated urine", "It strengthens the muscles responsible for controlling urination"),
                Q("Which organ stores urine before it leaves the body?",
                  "Urinary bladder",
                  "Kidneys", "Ureters", "Urethra"),
            ]},
            {"title": "Cavities", "questions": [
                Q("What is the main cause of dental cavities?", "Bacteria in the mouth produce acids that damage tooth enamel",
                  "The teeth lose minerals because the body produces too much saliva", "The gums become inflamed and gradually weaken the tooth roots", "The teeth become softer when exposed to cold food and drinks"),
                Q("How does eating sugary foods frequently increase the risk of cavities?",
                  "Mouth bacteria use sugar to produce acids that attack tooth enamel",
                  "Sugar directly dissolves the protective enamel layer when it touches the teeth", "Sugar reduces the amount of calcium transported through the bloodstream", "Sugar causes the gums to produce excess fluid around the teeth"),
                Q("Which practice helps reduce the risk of developing cavities?", "Brushing twice daily with fluoride toothpaste and cleaning between the teeth",
                  "Rinsing the mouth with water only after consuming sugary foods", "Brushing the teeth immediately after every acidic meal", "Using mouthwash regularly instead of brushing and flossing"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 2
    {
        "name": "Infections & Common Illnesses",
        "quizzes": [
            {"title": "Fever", "questions": [
                Q('What is a fever usually a sign of?', 'The body is fighting germs', 'The body is cooling itself after exercise', 'The body is adjusting to a change in hormone levels', 'The body is reacting to physical exertion'),
                Q('What happens to your body temperature when you have a fever?', 'It goes higher than normal', 'It becomes lower than normal', 'It remains within the usual range', 'It fluctuates only during sleep'),
                Q('What is a good thing to do when you have a fever?', 'Rest and drink plenty of fluids', 'Wear several thick layers to trap body heat', 'Take antibiotics without medical advice', 'Avoid fluids until the temperature falls'),
            ]},
            {"title": "Virus?", "questions": [
                Q('What is a virus?', 'A tiny germ that can make you sick', 'A tiny living cell that can reproduce on its own', 'A type of bacterium that can live independently', 'A microscopic fungus that grows on damp surfaces'),
                Q('Which of these illnesses is caused by a virus?', 'The common cold', 'Strep throat', 'Strep throat', 'Ringworm'),
                Q('What is a good way to avoid spreading viruses?', 'Washing your hands often', 'Take antibiotics whenever you have a cold', 'Share personal items only with close friends', 'Take antibiotics to prevent viral infections'),
            ]},
            {"title": "Chickenpox", "questions": [
                Q('What causes chickenpox?', 'A virus', 'A reaction to eating contaminated food', 'A bacterial infection entering through a skin wound', 'An allergic reaction to foods or medicines'),
                Q('What is a common sign of chickenpox?', 'Itchy red spots and blisters on the skin', 'A dry cough without any skin changes', 'A flat rash that appears only on the palms', 'Painful swelling limited to the joints'),
                Q('What should you try NOT to do if you have chickenpox?', 'Scratch the blisters', 'Drink plenty of water', 'Break the blisters to help them dry faster', 'Stop drinking fluids until the rash disappears'),
            ]},
            {"title": "Dengue", "questions": [
                Q('How do people get dengue fever?', 'From the bite of an infected mosquito', 'By breathing in droplets from an infected person', 'Direct contact with someone who has dengue', 'Eating food prepared by someone with dengue'),
                Q('What is a common sign of dengue?', 'High fever, headache, and body aches', 'A persistent cough with ear pain', 'A persistent cough with ear pain', 'A painless skin patch with no other symptoms'),
                Q('How can you help prevent dengue?', 'Get rid of standing water where mosquitoes lay eggs', 'Take antibiotics before mosquito season begins', 'Keep open containers of water around the home', 'Use antibiotics to prevent mosquito-borne infection'),
            ]},
            {"title": "Tetanus", "questions": [
                Q('What causes tetanus?', 'Bacteria that can enter the body through a dirty cut or wound', 'A virus transmitted through the air', 'A virus spread through coughing and sneezing', 'A fungus that grows on the surface of the skin'),
                Q('What is a sign of tetanus?', 'Painful muscle stiffness, especially in the jaw', 'A mild stomach ache after eating', 'A runny nose and watery eyes', 'Mild itching around the ankles'),
                Q('How can you prevent tetanus?', 'Get the tetanus vaccine and clean cuts properly', 'Avoid all outdoor activities where cuts might happen', 'Cover every wound without cleaning it', 'Use antibiotics instead of vaccination for long-term protection'),
            ]},
            {"title": "Rabies", "questions": [
                Q('How do people usually get rabies?', 'From the bite or scratch of an infected animal', 'By eating food prepared by an infected animal', 'By sharing food or drinks with an infected person', 'Through mosquito bites or contaminated water'),
                Q('Which animals can spread rabies?', 'Dogs, bats, and other mammals', 'Mosquitoes, ticks and other insects', 'Fish, reptiles and insects', 'Only domestic cats'),
                Q('What should you do right away if an animal bites you?', 'Wash the wound with soap and water and see a doctor', 'Wait a few days to see whether the wound becomes painful', 'Wait for symptoms before contacting a health professional', 'Cover the wound without washing it'),
            ]},
            {"title": "Mouth Ulcer", "questions": [
                Q('What is a mouth ulcer?', 'A small, painful sore inside the mouth', 'A hard lump that forms on the outside of the cheek', 'A bacterial coating that forms on the surface of the tongue', 'A swollen salivary gland beneath the jaw'),
                Q('What can make a mouth ulcer more painful?', 'Spicy or acidic foods', 'Cold, plain water', 'Drinking plain water usually damages the sore', 'Soft foods cause the ulcer to spread'),
                Q('What can help a mouth ulcer heal?', 'Keeping your mouth clean and avoiding spicy foods', 'Scrub the sore firmly when brushing your teeth', 'Pick at the ulcer to remove the damaged tissue', 'Stop brushing the teeth until it disappears'),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 3
    {
        "name": "Heart & Circulation",
        "quizzes": [
            {"title": "Fainting", "questions": [
                Q('What is fainting?', 'A short loss of consciousness, or "passing out"', 'A sudden loss of balance while remaining fully conscious', 'A short period when the brain uses more oxygen than usual', 'A sudden loss of muscle strength while consciousness remains normal'),
                Q('What usually causes fainting?', 'Not enough blood or oxygen reaching the brain for a moment', 'A sudden increase in blood flow to the brain', 'A brief rise in blood sugar sends extra blood to the brain', 'The lungs temporarily stop producing oxygen during digestion'),
                Q('What can make a person more likely to faint?', 'Dehydration, stress, or standing up too quickly', 'Getting enough sleep and drinking enough water', 'Eating a balanced meal or taking a short walk', 'Sleeping well or drinking enough fluids'),
            ]},
            {"title": "Cardiac Arrest", "questions": [
                Q('What happens in cardiac arrest?', 'The heart suddenly stops beating properly', 'The heart pumps faster than usual to meet the body’s needs', 'A blood vessel supplying the heart becomes narrowed over time', 'The heart muscle becomes temporarily inflamed after exercise'),
                Q('What is a sign of cardiac arrest?', "The person suddenly collapses, is unresponsive, and isn't breathing normally", 'A person has a mild headache but responds normally', 'Chest discomfort while remaining alert and breathing normally', 'Gradual tiredness with a mild headache'),
                Q('What should you do if you see someone in cardiac arrest?', 'Call emergency services right away and get an adult to help', 'Give the person something to eat to restore their energy', 'Give the person food or water and let them rest', 'Wait several minutes to see whether they wake up'),
            ]},
            {"title": "Heart Attack", "questions": [
                Q('What happens in a heart attack?', 'Blood flow to part of the heart is blocked', 'The heart’s electrical rhythm briefly speeds up during exercise', 'The heart suddenly stops producing electrical signals', 'The heart beats faster to deliver extra oxygen during exercise'),
                Q('What is a common sign of a heart attack?', 'Chest pain or pressure', 'An itchy rash on the arms', 'A sharp pain limited to one finger', 'A mild itch around the chest without other symptoms'),
                Q('What can help keep your heart healthy?', 'Healthy food and regular exercise', 'Avoid drinking water during physical activity', 'Avoid all physical activity to reduce the heart’s workload', 'Use supplements instead of prescribed heart medicines'),
            ]},
            {"title": "Blood Pressure", "questions": [
                Q('What is blood pressure?', 'The force of blood pushing against the walls of blood vessels', 'The number of times the heart beats in one minute', 'The amount of blood held inside the heart at one time', 'The speed at which the heart muscle relaxes between beats'),
                Q('Which device measures blood pressure?', 'Blood pressure monitor (sphygmomanometer)', 'A thermometer that checks body temperature', 'A pulse oximeter', 'A thermometer'),
                Q('What can help keep blood pressure healthy?', 'Eating less salt and exercising regularly', 'Add extra salt to every meal', 'Increase salty foods to help the blood hold more water', 'Stop prescribed medication once readings improve'),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 4
    {
        "name": "Health Conditions & Body Changes",
        "quizzes": [
            {"title": "Asthma", "questions": [
                Q('What does asthma affect?', 'The airways in the lungs', 'The digestive system and how it absorbs food', 'The air sacs where oxygen enters the blood', 'The muscles that control the movement of the ribs'),
                Q('What happens to the airways during an asthma attack?', 'They become narrow and swollen, making it hard to breathe', 'The lungs stop making red blood cells', 'The air sacs fill with fluid and stop exchanging gases', 'The diaphragm becomes temporarily unable to contract'),
                Q('Which of these can trigger asthma?', 'Dust, smoke, and pollen', 'Eating foods that contain fibre', 'Cold foods, bright lights or loud sounds', 'High-fibre foods, dehydration or lack of sleep'),
            ]},
            {"title": "Allergies", "questions": [
                Q('What is an allergy?', 'When the body overreacts to something harmless, like pollen or dust', 'An infection caused by harmful germs', 'A condition in which the body cannot digest certain nutrients', 'An infection caused by bacteria entering the bloodstream'),
                Q('Which of these can cause an allergic reaction?', 'Pollen, certain foods, or pet fur', 'A broken bone or muscle strain', 'Low temperatures, physical activity or lack of sleep', 'Minerals in drinking water or changes in blood pressure'),
                Q('What should you do if you have a serious allergic reaction, like trouble breathing or a swollen face?', 'Get help from a grown-up or doctor right away', 'Lie down and wait for the symptoms to disappear without telling anyone', 'Wait to see whether breathing difficulty settles on its own', 'Drink water and avoid moving for the rest of the day'),
            ]},
            {"title": "Migraine", "questions": [
                Q('What is a migraine?', 'A strong, throbbing headache that can last for hours or even days', 'A short episode of dizziness caused only by dehydration', 'A headache caused only by tension in the scalp muscles', 'A sinus infection that causes pressure around the forehead'),
                Q('Which of these can happen during a migraine?', 'Sensitivity to light and sound, or feeling sick', 'A broken bone or sudden skin infection', 'Fever, a productive cough or swollen lymph nodes', 'Joint swelling, itchy skin or hearing loss'),
                Q('What can help when you have a migraine?', 'Resting in a quiet, dark room and telling a grown-up', 'Stay in a brightly lit, noisy room and continue strenuous activity', 'Continue strenuous activity to distract from the pain', 'Use bright screens and skip meals until the pain passes'),
            ]},
            {"title": "Epilepsy", "questions": [
                Q('What is epilepsy?', 'A brain condition that can cause seizures', 'A disease that affects only the bones and joints', 'A condition caused by a temporary drop in blood sugar only', 'An infection that causes inflammation of the spinal cord'),
                Q('What is a seizure?', 'A sudden burst of electrical activity in the brain', 'A sudden infection that causes a high fever', 'A sudden increase in blood pressure in the legs', 'A brief interruption of digestion in the stomach'),
                Q('What should you do if someone is having a seizure?', 'Stay calm, keep them safe, and call for adult help', 'Hold the person down to stop their movements', 'Hold their arms and legs down to stop the movements', 'Put an object between their teeth to protect the tongue'),
            ]},
            {"title": "Diabetes", "questions": [
                Q('What does diabetes affect?', 'How the body handles sugar (glucose) in the blood', 'The body’s ability to digest proteins', 'How the body controls the amount of oxygen in the blood', 'How the body produces digestive acid'),
                Q("Which hormone helps move sugar from the blood into the body's cells?", 'Insulin', 'Adrenaline', 'Glucagon', 'Thyroxine'),
                Q('What helps lower the risk of type 2 diabetes?', 'Healthy eating and regular exercise', 'Avoid all exercise and eat sugary snacks frequently', 'Avoiding all carbohydrates and skipping meals', 'Taking insulin even when it has not been prescribed'),
            ]},
            {"title": "Kidney Stones", "questions": [
                Q('What is a kidney stone?', 'A hard lump made of minerals and salts that forms in the kidney', 'A small infection that develops inside the bladder', 'A bacterial infection that develops inside the bladder', 'A soft tissue growth that forms on the outside of the kidney'),
                Q('What is a common sign of a kidney stone?', 'Sharp pain in the back or side, or pain when peeing', 'A painless rash that appears on the arms', 'A mild cough with a sore throat', 'A gradual loss of hearing in one ear'),
                Q('What can help prevent kidney stones?', 'Drinking plenty of water', 'Drink very little water throughout the day', 'Avoid fluids so the kidneys produce less urine', 'Increase salt intake to prevent minerals from collecting'),
            ]},
            {"title": "Pimples", "questions": [
                Q('What causes pimples?', 'Clogged skin pores with oil and dead skin cells', 'A lack of calcium in the bones', 'Sweat glands stop producing enough moisture', 'The skin produces too little melanin after sun exposure'),
                Q('When do pimples often appear more?', 'During puberty, when hormones change', 'When the skin produces less oil than usual', 'Only after eating oily foods', 'Only when the skin is exposed to cold weather'),
                Q('What should you NOT do with a pimple?', 'Squeeze or pick at it', 'Wash your face gently with a mild cleanser', 'Scrub the area forcefully several times a day', 'Apply strong household cleaning products to dry the spot'),
            ]},
            {"title": "Period", "questions": [
                Q('What is a period (menstruation)?', 'A monthly shedding of the lining of the uterus, which comes out as blood', 'The release of an egg from an ovary', 'The ovaries release an egg during the menstrual cycle', 'The body releases an excess of hormones through the blood'),
                Q('Around what age do girls usually start getting their periods?', 'Between 9 and 15 years old', 'Usually between 5 and 8 years old', 'Usually between 5 and 8 years old', 'Usually between 16 and 20 years old'),
                Q('Is having a period normal and healthy?', "Yes, it's a normal part of growing up", 'No, it usually means the reproductive system is infected', 'No, it usually means the reproductive system is infected', 'Only if the bleeding happens at the same date each month'),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 5
    {
        "name": "Mental Health & Learning",
        "quizzes": [
            {"title": "Depression", "questions": [
                Q('What is depression?', 'A health condition that causes ongoing sadness and loss of interest in things', 'A short moment of disappointment that quickly goes away', 'A short-term emotional reaction that always passes within a day', 'A personality trait that makes someone prefer being alone'),
                Q('Which of these can be a sign of depression?', 'Feeling sad or empty for a long time', 'Feeling excited and energetic all the time', 'A brief feeling of disappointment after a difficult day', 'Increased energy and unusually high confidence every day'),
                Q('What should you do if you or a friend feels very sad for a long time?', 'Talk to a trusted adult, parent, or doctor', 'Keep the feelings secret and avoid talking to anyone', 'Tell them to simply think positively and avoid discussing it', 'Assume they will recover without support if left alone'),
            ]},
            {"title": "Autism Spectrum (ASD)", "questions": [
                Q('What is autism spectrum disorder (ASD)?', 'A condition that affects how a person communicates, learns, and interacts with others', 'An illness caused by a virus that affects the lungs', 'A mental illness that develops after a stressful event', 'A learning disorder that affects reading and spelling only'),
                Q('Why is it called a "spectrum"?', 'Because it looks different and affects each person differently', 'Everyone with autism has exactly the same strengths and needs', 'Everyone has the same traits but at different levels', "It describes how severe a person's physical illness is"),
                Q('How should we treat people with autism?', 'With kindness, patience, and respect', 'Assume they all communicate and learn in the same way', 'Expect everyone with autism to respond in the same way', 'Avoid including them in group activities to prevent discomfort'),
            ]},
            {"title": "Alzheimer's", "questions": [
                Q("What is Alzheimer's disease?", 'A brain disease that causes memory loss and confusion', 'A temporary stomach illness that affects digestion', 'A normal part of ageing that happens to everyone', 'A temporary infection that causes short-term confusion'),
                Q("Who is most often affected by Alzheimer's?", 'Older people', 'It mainly affects babies and toddlers', 'It mainly affects school-age children', 'It occurs only in people with a family history'),
                Q("How should we treat someone with Alzheimer's?", 'With patience, kindness, and understanding', 'Speak harshly when they forget something so they remember it', 'Correct every mistake immediately and test their memory often', 'Give several instructions at once to improve concentration'),
            ]},
            {"title": "Dyslexia", "questions": [
                Q('What is dyslexia?', 'A learning difference that makes reading and spelling harder', 'A hearing condition that makes quiet sounds difficult to detect', 'A condition that mainly affects hearing and sound recognition', 'A developmental condition that prevents a person from understanding numbers'),
                Q('Does dyslexia mean a person is not smart?', 'No, people with dyslexia can be very smart and creative', 'Yes, it means a person cannot learn new skills', 'Yes, it means a person cannot understand complex ideas', 'Yes, it means a person has below-average memory in every area'),
                Q('What can help a person with dyslexia learn better?', 'Extra practice and special teaching methods', 'Remove all reading support and expect them to learn without help', 'More copying from the board without additional guidance', 'Avoiding reading activities so mistakes do not occur'),
            ]},
            {"title": "Stuttering", "questions": [
                Q('What is stuttering?', 'A speech difference where sounds or words are repeated or get stuck', 'A condition that makes a person unable to hear speech', 'A language disorder that means someone does not understand words', 'A voice condition caused only by speaking too quietly'),
                Q('Does stuttering mean a person is not smart?', 'No, people who stutter can be just as smart as anyone', 'Yes, it means the person cannot understand instructions', 'Yes, it means the person has difficulty learning new information', 'Yes, it usually means the person cannot understand conversations'),
                Q('How should we act when someone stutters?', 'Be patient and let them finish speaking', 'Interrupt and finish their sentences for them', 'Finish their words to help them speak faster', 'Ask them to repeat the sentence until it is fluent'),
            ]},
            {"title": "Anger", "questions": [
                Q('What is anger?', 'A normal feeling everyone has sometimes', 'A physical illness caused by bacteria', 'A medical condition that always requires medication', 'A sign that a person cannot control any of their emotions'),
                Q('What is a healthy way to handle anger?', 'Take deep breaths and calm down', 'Break objects to release frustration', 'Send an angry message immediately to release the feeling', 'Keep arguing until the other person agrees'),
                Q('What can you do after you feel calm?', 'Talk about your feelings with a trusted person', 'Start the argument again before listening to anyone', 'Pretend nothing happened and refuse to discuss it', 'Blame someone else before understanding the situation'),
            ]},
        ],
    },
    # ------------------------------------------------------------------ 6
    {
        "name": "First Aid & Emergencies",
        "quizzes": [
            {"title": "Finger Cuts", "questions": [
                Q('What is the first thing to do for a small finger cut?', 'Wash your hands, then gently press on the cut to stop the bleeding', 'Apply a thick layer of ointment before checking the wound', 'Rinse the cut immediately while rubbing the wound firmly', 'Apply antiseptic directly before checking the bleeding'),
                Q('How should you clean a small cut?', 'Rinse it with clean running water', 'Wipe the wound with a dry tissue without rinsing it', 'Scrub the wound with soap inside the cut', 'Use alcohol or hydrogen peroxide repeatedly to flush it'),
                Q('What should you do after cleaning the cut?', 'Cover it with a clean bandage', 'Rub dirt into the wound to help form a scab', 'Leave it uncovered so a scab forms more quickly', 'Apply powder before covering it with a bandage'),
            ]},
            {"title": "Broken Bone", "questions": [
                Q('What does the body do first after a bone breaks?', 'A blood clot forms around the break', 'The broken pieces immediately fuse together without any repair process', 'The bone immediately returns to its original shape', 'The surrounding muscle turns into new bone tissue'),
                Q('What do new bone cells do during healing?', 'They build new bone to join the broken pieces together', 'They turn the nearby muscles into cartilage', 'They remove all bone tissue around the fracture', 'They prevent blood vessels from reaching the injured area'),
                Q('What helps a broken bone heal properly?', 'A cast or splint to keep it still, plus rest', 'Keep moving the injured bone so it does not become stiff', 'Start putting full weight on it as soon as pain decreases', 'Remove the cast whenever the area feels uncomfortable'),
            ]},
            {"title": "Choking", "questions": [
                Q('What is choking?', "When food or an object blocks the airway so air can't pass", 'When the stomach cannot digest food properly', 'The throat becomes irritated but air can still pass normally', 'The food pipe becomes blocked while breathing remains unaffected'),
                Q('What is a common sign of choking?', 'Being unable to cough, speak, or breathe', 'A person can speak in full sentences and breathe comfortably', 'The person can speak clearly but has a mild sore throat', 'The person sneezes repeatedly and has watery eyes'),
                Q('What should you do if someone is choking?', 'Call for adult help right away and get emergency help', 'Give the person food to push the blockage down', 'Offer a drink of water to push the object down', 'Put fingers into the mouth to search blindly for the object'),
            ]},
            {"title": "Drowning", "questions": [
                Q('What is drowning?', 'When water gets into the airway and makes it hard to breathe', 'Feeling cold after swimming while breathing normally', 'Swallowing water that causes temporary stomach discomfort', 'Getting cold after swimming without breathing problems'),
                Q('How can you stay safe around water?', 'Swim with an adult nearby and learn to swim', 'Swim alone in deep water if you are confident', 'Swim alone if the water looks calm', 'Enter unfamiliar water without checking depth or currents'),
                Q('What should you do if you see someone drowning?', 'Call for adult or lifeguard help right away', 'Jump into the water immediately, even if you cannot swim well', 'Jump into deep water even if you are not trained to rescue', 'Wait until the person reaches the shore without assistance'),
            ]},
            {"title": "Bee Sting", "questions": [
                Q('What does a bee often leave behind after stinging?', 'Its stinger', 'Its wings', 'A bee usually leaves its wings attached to the skin', 'A bee injects a small piece of its leg under the skin'),
                Q('What should you do with the stinger?', 'Scrape it out quickly with a flat edge, like a card', 'Leave it in place until the swelling goes away', 'Squeeze the venom sac repeatedly before removing it', 'Cut the skin around the sting to release the venom'),
                Q('What can help reduce pain and swelling?', 'A cold pack or ice wrapped in a cloth', 'Apply a hot cloth and rub the sting firmly', 'Apply heat and massage the area firmly', 'Scratch the area to improve circulation'),
            ]},
            {"title": "Wasp Sting", "questions": [
                Q('What is a common sign of a wasp sting?', 'Pain, redness, and swelling where you were stung', 'A painless bruise that appears weeks later', 'A painless blister that always appears several days later', 'A loss of sensation throughout the entire body'),
                Q('What can you do first for a wasp sting?', 'Wash the area with soap and water and apply a cold pack', 'Scratch the area repeatedly to remove the venom', 'Apply soil or plant sap to draw out the venom', 'Rub the sting firmly to spread the swelling'),
                Q('When should you get medical help right away?', 'If there is trouble breathing or a swollen face or throat', 'Only if the sting is still painful the next morning', 'Wait several hours if the person feels faint after the sting', 'Treat facial or throat swelling at home with a cold cloth only'),
            ]},
            {"title": "Heat Wave", "questions": [
                Q('What is a heat wave?', 'A period of unusually hot weather lasting days', 'A period of unusually cold weather lasting several days', 'A sudden drop in temperature accompanied by strong winds', 'A brief increase in humidity after rainfall'),
                Q('What can happen if you get too hot?', 'Heat exhaustion or heatstroke', 'Your body temperature drops dangerously low', 'A drop in body temperature and slower breathing', 'A temporary increase in bone strength'),
                Q('How can you stay safe in a heat wave?', 'Drink lots of water and stay in the shade or a cool place', 'Spend long periods exercising outdoors at midday', 'Exercise outdoors during the hottest part of the day', 'Stay inside a parked car with the windows closed'),
            ]},
            {"title": "Stampede", "questions": [
                Q('What is a stampede?', 'A sudden rush of a panicked crowd or herd of animals', 'A carefully organised line of people entering a venue', 'A planned movement of people through a wide entrance', 'A slow movement of people leaving an event in an orderly way'),
                Q('What can cause a crowd stampede?', 'Panic, fear, or overcrowding in a small space', 'Wide exits, clear signs and calm crowd movement', 'Clear exits and good crowd management', 'A quiet venue with enough room for people to move'),
                Q('What should you do if you are caught in a moving crowd?', 'Stay calm, stay on your feet, and move with the crowd toward the edge or an exit', 'Stop suddenly and push against the people around you', 'Push against the crowd and stop suddenly', 'Bend down to pick up belongings while the crowd is moving'),
            ]},
        ],
    },
]


# ---------------------------------------------------------------------------
# 3. Video data
#    V(field index, title, YouTube id, quiz title used by "Take the quiz")
# ---------------------------------------------------------------------------
def V(f, title, vid, quiz):
    return {"f": f, "title": title, "id": vid, "quiz": quiz}


VIDEOS = [
    # 0 Body Systems & Organs
    V(0, "Immune System", "azE3rv5l28Y", "Immune System"),
    V(0, "Digestive System", "ZBZWgrfZFbU", "Digestive System"),
    V(0, "Gut", "4zLU2UE90jM", "Gut"),
    V(0, "Liver Function", "IMzFgyrUXnE", "Liver Function"),
    V(0, "Respiratory System", "mOKmjYwfDGU", "Respiratory System"),
    V(0, "Urinary Function", "dZREDWD_5bA", "Urinary System"),
    V(0, "How the Brain Works", "ndDpjT0_IM0", "Brain"),
    V(0, "Hormones", "_nyvBUmIwhI", "Hormones"),
    V(0, "Body Parts", "jd3bWUAa9qM", "Body Parts"),
    V(0, "How Muscles Grow", "Vnj9Ay6xmOk", "Muscles"),
    # 1 Nutrition & Healthy Habits
    V(1, "Drink Water", "31F0laJjyy8", "Drink Water"),
    V(1, "Food Pyramid", "tsgyWIsYvxs", "Food Pyramid"),
    V(1, "Urine Color", "ka85yQcA524", "Urine Color"),
    V(1, "Constipation", "TK0ZF7FNxsU", "Constipation"),
    V(1, "Holding Urine", "BrCIcqS1yEg", "Holding Urine"),
    V(1, "Cavities", "3ZHYQ6f1BhU", "Cavities"),
    # 2 Infections & Common Illnesses
    V(2, "Fever", "BqOaG9VuP_I", "Fever"),
    V(2, "What is a Virus?", "YS7vsBgWszI", "Virus?"),
    V(2, "Chickenpox", "xNc4kEt4pN0", "Chickenpox"),
    V(2, "Dengue", "Oy1eQQZQZvs", "Dengue"),
    V(2, "Tetanus", "S6rogdxMGww", "Tetanus"),
    V(2, "Rabies", "EAhqjbWpLSI", "Rabies"),
    V(2, "Mouth Ulcer", "ScAq1VgTml0", "Mouth Ulcer"),
    # 3 Heart & Circulation
    V(3, "Why We Faint", "2-Dv9P6gLYY", "Fainting"),
    V(3, "Cardiac Arrest", "41kcmMJQ2ds", "Cardiac Arrest"),
    V(3, "Heart Attack", "jP0qT6GpBVY", "Heart Attack"),
    V(3, "Blood Pressure", "2HTZs51OYwo", "Blood Pressure"),
    # 4 Health Conditions & Body Changes
    V(4, "Asthma", "s1R0dL1VB0I", "Asthma"),
    V(4, "Allergies", "sM3FDsMAMdc", "Allergies"),
    V(4, "Migraine", "wRGxUc-AuUM", "Migraine"),
    V(4, "Epilepsy", "AaBgkBEA9eM", "Epilepsy"),
    V(4, "Diabetes", "d86DofYpkrY", "Diabetes"),
    V(4, "Kidney Stones", "xmbpPWIV0VU", "Kidney Stones"),
    V(4, "Pimples", "SPQt5v5Xsg8", "Pimples"),
    V(4, "Period", "PeL_XtBrOxw", "Period"),
    # 5 Mental Health & Learning
    V(5, "Depression", "0hxFR6tezAc", "Depression"),
    V(5, "Autism Spectrum (ASD)", "d2mlWUzA0B4", "Autism Spectrum (ASD)"),
    V(5, "Alzheimer's", "5dmqaH-MlA0", "Alzheimer's"),
    V(5, "Dyslexia", "65psPXWzNic", "Dyslexia"),
    V(5, "Stuttering", "juMxqemIlpU", "Stuttering"),
    V(5, "Anger", "clwt7iXF1Mg", "Anger"),
    # 6 First Aid & Emergencies
    V(6, "First Aid: Finger Cuts", "Z3XN4GWANRM", "Finger Cuts"),
    V(6, "How a Broken Bone Heals", "yovH2-Uw7i8", "Broken Bone"),
    V(6, "Choking", "oSZG9JHdngM", "Choking"),
    V(6, "Drowning", "WKu7_Fwf3PI", "Drowning"),
    V(6, "Bee Sting", "H_wj50ox8OY", "Bee Sting"),
    V(6, "Wasp Sting", "8Fz3qvNvLO8", "Wasp Sting"),
    V(6, "Heat Wave", "ARB6R51iQ_k", "Heat Wave"),
    V(6, "Stampede", "MSiw9ZGdtSQ", "Stampede"),
]

# Warn in the terminal if a video points at a quiz title that does not exist.
_known = {(fi, z["title"]) for fi, f in enumerate(FIELDS) for z in f["quizzes"]}
for _v in VIDEOS:
    if (_v["f"], _v["quiz"]) not in _known:
        print("[AiJaga] WARNING: no quiz titled %r in field %d (video %r)" % (_v["quiz"], _v["f"], _v["title"]))


def videos_in_field(fi):
    return [v for v in VIDEOS if v["f"] == fi]


def quiz_index(fi, title):
    for qi, z in enumerate(FIELDS[fi]["quizzes"]):
        if z["title"] == title:
            return qi
    return -1


# ---------------------------------------------------------------------------
# 4. Chat text
# ---------------------------------------------------------------------------
WELCOME = (f"Hi, I'm {DOCTOR}! Ask me a health question by typing below, "
           "tap a topic, or tap + to add a photo or a voice note.")
CHAT_INSTRUCTIONS = (
    "You are Dr. Azmi, AiJaga's AI health education assistant in Malaysia. "
    "Answer in the user's language using short, accessible plain text. "
    "Provide general health information. Do not claim to be a clinician, diagnose, "
    "or prescribe. For signs of an emergency, advise calling local emergency services "
    "(999 in Malaysia) immediately. Do not request identifying information."
)
DISCLAIMER = "AiJaga shares general health information, not a diagnosis. In an emergency, call 999."
EMERGENCY_NOTE = "If this is an emergency, call 999 now or get a nearby adult to help."

# ---------------------------------------------------------------------------
# 5. Offline "topic library" brain
#    Matches a question to a quiz topic and answers from the quiz facts.
#    Used when there is no Agnes API key or the AI service fails.
# ---------------------------------------------------------------------------
STOP = set("what whats why how does are the and for with can you about tell work works have has get when should "
           "your from that this there help please feel cause causes caused mean means body some not too very any "
           "who was were will into their them then than".split())
ALIAS = {
    "headache": "migraine", "acne": "pimples", "zit": "pimples", "zits": "pimples", "breathe": "respiratory",
    "breathing": "respiratory", "lung": "respiratory", "lungs": "respiratory", "poop": "constipation",
    "poo": "constipation", "pee": "urine", "wee": "urine", "sugar": "diabetes", "tooth": "cavities",
    "teeth": "cavities", "mosquito": "dengue", "mosquitoes": "dengue", "seizure": "epilepsy",
    "seizures": "epilepsy", "memory": "alzheimer", "stomach": "digestive", "flu": "virus", "cold": "virus",
    "covid": "virus", "dog": "rabies", "hot": "heat", "crowd": "stampede", "sad": "depression",
    "angry": "anger", "faint": "faint", "fainting": "faint", "dizzy": "faint", "rash": "chickenpox",
    "cramps": "period", "menstruation": "period", "liver": "liver", "kidney": "kidney", "heartbeat": "heart",
    "bp": "blood pressure",
}
EMERGENCY = re.compile(r"(emergency|can'?t breathe|cannot breathe|not breathing|chest pain|unconscious|passed out|"
                       r"heavy bleeding|bleeding a lot|overdose|poison|suicid|kill myself|self[- ]harm)", re.I)
GREETING = re.compile(r"^\s*(hi|hello|hey|hai|salam|assalam)\b", re.I)


def _stem(w):
    w = re.sub(r"[^a-z]", "", w)
    if len(w) > 5:
        w = re.sub(r"ing$", "", w)
    w = re.sub(r"e$", "", re.sub(r"s$", "", w))
    return w[:5]


def _tokens(s):
    words = [w for w in re.split(r"[^a-z]+", s.lower()) if len(w) >= 3 and w not in STOP]
    return [t for t in (_stem(w) for w in words) if t]


TOPIC_INDEX = [{"fi": fi, "qi": qi, "title": z["title"], "stems": set(_tokens(z["title"]))}
               for fi, f in enumerate(FIELDS) for qi, z in enumerate(f["quizzes"])]


def find_topic(text):
    wanted = set()
    for w in re.split(r"[^a-z]+", text.lower().replace("'", "")):
        if not w:
            continue
        wanted.update(_tokens(w))
        if w in ALIAS:
            wanted.update(_tokens(ALIAS[w]))
    best, best_score = None, 0
    for item in TOPIC_INDEX:
        score = len(item["stems"] & wanted)
        if score > best_score:
            best, best_score = item, score
    return best


def random_topics(n=4):
    return [t["title"] for t in random.sample(TOPIC_INDEX, n)]


def library_reply(text, hit, emergency):
    """Answer from the quiz facts. Returns (reply_text, chips)."""
    if hit:
        quiz = FIELDS[hit["fi"]]["quizzes"][hit["qi"]]
        lines = [f"Here's what I know about {quiz['title']}:"]
        for q in quiz["questions"][:Q_PER]:
            lines.append(f"- {q['q']}")
            lines.append(f"→ {q['answer']}")
        lines.append("General health information, not a diagnosis.")
        return "\n".join(lines), []
    if emergency:
        return ("I can only share general information here. Please get help from a trusted adult "
                "or call 999."), []
    if GREETING.search(text):
        return "Hello! What would you like to know? You can ask about:", random_topics()
    return "I don't know that one yet. I can help with topics from the AiJaga library, like:", random_topics()


# ---------------------------------------------------------------------------
# 6. Pixel art (SVG drawings made of little squares)
# ---------------------------------------------------------------------------
LOGO_SVG = """
<svg width="{w}" height="{h}" viewBox="0 0 17 15" shape-rendering="crispEdges" role="img" aria-label="AiJaga logo">
<rect x="3" y="2" width="4" height="1" fill="#3E8EC2"/><rect x="2" y="3" width="6" height="3" fill="#3E8EC2"/>
<rect x="3" y="6" width="4" height="1" fill="#3E8EC2"/>
<rect x="1" y="8" width="8" height="1" fill="#3E8EC2"/><rect x="0" y="9" width="10" height="6" fill="#3E8EC2"/>
<rect x="3" y="8" width="1" height="5" fill="#1C2B33"/><rect x="6" y="8" width="1" height="3" fill="#1C2B33"/>
<rect x="2" y="12" width="3" height="2" fill="#1C2B33"/><rect x="3" y="12" width="1" height="1" fill="#3E8EC2"/>
<rect x="5" y="11" width="3" height="3" fill="#1C2B33"/><rect x="6" y="12" width="1" height="1" fill="#3E8EC2"/>
<rect x="10" y="0" width="2" height="1" fill="#E0405E"/><rect x="13" y="0" width="2" height="1" fill="#E0405E"/>
<rect x="9" y="1" width="7" height="2" fill="#E0405E"/><rect x="10" y="3" width="5" height="1" fill="#E0405E"/>
<rect x="11" y="4" width="3" height="1" fill="#E0405E"/><rect x="12" y="5" width="1" height="1" fill="#E0405E"/>
<rect x="10" y="1" width="1" height="1" fill="#FF8FA3"/>
</svg>
"""

DOCTOR_SVG = """
<svg width="{w}" height="{h}" viewBox="0 0 16 20" shape-rendering="crispEdges" role="img" aria-label="Dr. Azmi">
<rect x="6" y="0" width="4" height="1" fill="#C9D3D0"/><rect x="7" y="0" width="2" height="1" fill="#E36F52"/>
<rect x="3" y="1" width="10" height="1" fill="#1C2B33"/>
<rect x="3" y="2" width="1" height="5" fill="#1C2B33"/><rect x="12" y="2" width="1" height="5" fill="#1C2B33"/>
<rect x="4" y="1" width="8" height="2" fill="#4A2E22"/>
<rect x="4" y="3" width="8" height="4" fill="#F2C29B"/>
<rect x="6" y="4" width="1" height="2" fill="#1C2B33"/><rect x="9" y="4" width="1" height="2" fill="#1C2B33"/>
<rect x="5" y="5" width="1" height="1" fill="#E36F52"/><rect x="10" y="5" width="1" height="1" fill="#E36F52"/>
<rect x="4" y="7" width="8" height="1" fill="#1C2B33"/><rect x="7" y="6" width="2" height="1" fill="#1C2B33"/>
<rect x="7" y="8" width="2" height="1" fill="#F2C29B"/>
<rect x="3" y="8" width="10" height="11" fill="#1C2B33"/>
<rect x="4" y="9" width="8" height="9" fill="#FFFFFF"/>
<rect x="5" y="8" width="6" height="4" fill="#1C2B33"/><rect x="6" y="9" width="4" height="3" fill="#2D6A5C"/>
<rect x="7" y="9" width="2" height="1" fill="#F2C29B"/>
<rect x="7" y="12" width="2" height="2" fill="#E36F52"/>
<rect x="10" y="12" width="2" height="1" fill="#2D6A5C"/>
</svg>
"""

MINI_DOCTOR_SVG = """
<svg width="34" height="34" viewBox="0 0 8 8" shape-rendering="crispEdges" aria-hidden="true">
<rect x="1" y="0" width="6" height="2" fill="#4A2E22"/><rect x="1" y="2" width="6" height="3" fill="#F2C29B"/>
<rect x="2" y="3" width="1" height="1" fill="#1C2B33"/><rect x="5" y="3" width="1" height="1" fill="#1C2B33"/>
<rect x="0" y="5" width="8" height="3" fill="#FFFFFF"/><rect x="3" y="5" width="2" height="3" fill="#2D6A5C"/>
</svg>
"""

# Doctor with a changeable mouth (used on the quiz result screen).
DOC_PAL = {"h": "#5b3a29", "s": "#f2b88f", "b": "#1b2a35", "e": "#1b2a35", "w": "#ffffff",
           "g": "#2d6a5a", "r": "#e07050", "m": "#b8433f", "k": "#cfd9d6"}


def pix(rows, pal, px):
    w, h = len(rows[0]), len(rows)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02" fill="{pal[c]}"/>'
                    for y, row in enumerate(rows) for x, c in enumerate(row) if c in pal)
    return (f'<svg viewBox="0 0 {w} {h}" width="{w * px}" height="{h * px}" shape-rendering="crispEdges" '
            f'aria-hidden="true" style="display:inline-block;image-rendering:pixelated">{rects}</svg>')


def mood_doctor(mood, px=10):
    mouth = {"happy": "bsmmmmsb", "ok": "bssmmssb", "flat": "bssssssb"}.get(mood, "bssmmssb")
    rows = ["......rr......", "....hhhhhh....", "...hhhhhhhh...", "...hssssssh...", "...sesssses...",
            "..." + mouth + "...", "...bbbbbbbb...", "....bbbbbb....", ".kwwwwggwwwwk.", "wwwwwwggwwwwww",
            "wwrwwwggwwwwww", "wwrwwwggwwwwww", "wwwrrwwggwwwww", "wwwwwwwwwwwwww", "wwwwwwwwwwwwww"]
    return pix(rows, DOC_PAL, px)


def svg_url(svg):
    """Turn an SVG string into something CSS can use as a background image."""
    return "url(\"data:image/svg+xml," + quote(" ".join(svg.split())) + "\")"


def esc(s):
    return html.escape(str(s))


# ---------------------------------------------------------------------------
# 7. Session state (remembers things between clicks)
# ---------------------------------------------------------------------------
DEFAULTS = {
    "page": "home",
    "theme": "bright",
    "messages": [{"role": "bot", "text": WELCOME, "chips": random_topics()}],
    "read_aloud": False,
    "speak": None,
    "chat_error": None,
    "chat_note": None,
    # quiz
    "xp": 0,
    "progress": {},          # "Field|Title" -> {"answered": n, "score": n}
    "q_field": 0, "q_topic": 0, "q_items": [], "q_i": 0, "q_pick": None, "q_score": 0,
    "celebrate": False,
    # video
    "v_field": 0, "v_i": 0, "video_seen": set(),
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, set, dict)) else value

S = st.session_state
C = THEMES[S.theme]


def go(page):
    S.page = page


def set_theme(name):
    S.theme = name


# ---------------------------------------------------------------------------
# 8. Retro "AiJaga TV" styling
# ---------------------------------------------------------------------------
def inject_css():
    play_icon = svg_url(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 12 9' shape-rendering='crispEdges'>"
        f"<rect width='12' height='9' fill='{C['ink']}'/><rect x='1' y='1' width='10' height='7' fill='{C['chip']}'/>"
        f"<rect x='4' y='2' width='1' height='5' fill='{C['coral']}'/><rect x='5' y='3' width='1' height='3' fill='{C['coral']}'/>"
        f"<rect x='6' y='4' width='1' height='1' fill='{C['coral']}'/></svg>")
    quiz_icon = svg_url(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='130' height='70' viewBox='0 0 13 7' shape-rendering='crispEdges'>"
        f"<rect x='1' y='0' width='1' height='1' fill='{C['coral']}'/><rect x='0' y='1' width='1' height='5' fill='{C['coral']}'/>"
        f"<rect x='1' y='6' width='1' height='1' fill='{C['coral']}'/>"
        f"<rect x='11' y='0' width='1' height='1' fill='{C['coral']}'/><rect x='12' y='1' width='1' height='5' fill='{C['coral']}'/>"
        f"<rect x='11' y='6' width='1' height='1' fill='{C['coral']}'/>"
        f"<rect x='5' y='0' width='3' height='1' fill='{C['ink']}'/><rect x='4' y='1' width='1' height='1' fill='{C['ink']}'/>"
        f"<rect x='8' y='1' width='1' height='2' fill='{C['ink']}'/><rect x='7' y='3' width='1' height='1' fill='{C['ink']}'/>"
        f"<rect x='6' y='4' width='1' height='1' fill='{C['ink']}'/><rect x='6' y='6' width='1' height='1' fill='{C['ink']}'/></svg>")

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Nunito:wght@500;600;700;800&display=swap');

#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}
.stApp {{ background: {C['page']}; }}
html, body, .stApp, p, label, li, input, textarea, .stMarkdown {{ font-family: 'Nunito', sans-serif; color: {C['ink']}; }}
.stApp [data-testid="stCaptionContainer"] p {{ color: {C['sub']}; }}

/* The TV body and screen */
.block-container {{
  max-width: 1240px; margin: 30px auto 0; padding: 26px 30px 30px !important;
  background-color: {C['screen']};
  background-image: repeating-linear-gradient(0deg, {C['scan']} 0 2px, transparent 2px 5px);
  border: 8px solid {C['frame_edge']}; border-radius: 28px;
  box-shadow: 0 0 0 26px {C['frame']}, 0 26px 0 26px {C['frame']};
}}

.pixel {{ font-family: 'Silkscreen', monospace; font-weight: 700; letter-spacing: 1px; }}
.sub {{ color: {C['sub']}; }}
h1, h2, h3 {{ font-family: 'Silkscreen', monospace !important; color: {C['ink']} !important; letter-spacing: 1px; }}
.page-title {{ text-align: center; font-size: 34px; margin: 18px 0 2px; }}
.page-sub {{ text-align: center; font-family: 'Silkscreen', monospace; font-size: 14px; letter-spacing: 3px;
             color: {C['sub']}; margin: 0 0 22px; }}

.card {{ background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 8px 8px 0 {C['ink']};
         padding: 20px 22px; margin-bottom: 18px; color: {C['ink']}; }}
.tag {{ display: inline-block; padding: 4px 12px; background: {C['coral']}; border: 3px solid {C['ink']};
        color: #1C2B33; font-family: 'Silkscreen', monospace; font-weight: 700; font-size: 13px; letter-spacing: 1px; }}
.logo {{ display: flex; align-items: center; gap: 12px; }}

/* Buttons: chunky pixel style */
.stButton > button, .stFormSubmitButton > button, [data-testid="stPopover"] button {{
  border: 3px solid {C['ink']} !important; border-radius: 0 !important;
  background: {C['chip']} !important; color: {C['ink']} !important;
  box-shadow: 4px 4px 0 {C['ink']}; font-weight: 700; min-height: 46px;
}}
.stButton > button:hover, [data-testid="stPopover"] button:hover {{ transform: translate(-2px, -2px); box-shadow: 6px 6px 0 {C['ink']}; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button {{
  background: {C['teal']} !important; color: {C['btn_text']} !important;
  font-family: 'Silkscreen', monospace; letter-spacing: 1px;
}}
.stButton > button p, .stFormSubmitButton > button p, [data-testid="stPopover"] button p {{ color: inherit !important; white-space: normal; }}

/* Text boxes */
.stTextInput input {{ border-radius: 0 !important; background: {C['card']} !important; color: {C['ink']} !important; font-size: 17px; }}
.stTextInput input::placeholder {{ color: {C['sub']}; opacity: .8; }}
.stTextInput > div > div {{ border: 3px solid {C['ink']} !important; border-radius: 0 !important; }}

/* Level / score bar */
.bar-label {{ font-family: 'Silkscreen', monospace; font-size: 12px; letter-spacing: 2px; color: {C['sub']}; }}
.score-bar {{ height: 18px; border: 3px solid {C['ink']}; background: {C['card']}; margin: 6px 0 4px; }}
.score-fill {{ height: 100%; background: {C['coral']}; transition: width .5s; }}

/* Speech bubble */
.bubble-hello {{ position: relative; background: {C['card']}; border: 4px solid {C['ink']};
                 box-shadow: 8px 8px 0 {C['ink']}; padding: 16px 22px; max-width: 520px; }}
.bubble-hello::before {{ content: ""; position: absolute; left: -22px; top: 14px; border: 11px solid transparent;
                         border-right-color: {C['ink']}; border-top-color: {C['ink']}; }}
.dots span {{ display: inline-block; width: 7px; height: 7px; margin-right: 6px; background: {C['coral']};
              animation: blink 1.2s infinite; }}
.dots span:nth-child(2) {{ animation-delay: .2s; }} .dots span:nth-child(3) {{ animation-delay: .4s; }}
@keyframes blink {{ 0%, 80%, 100% {{ opacity: .2; }} 40% {{ opacity: 1; }} }}

/* Chat panel */
.st-key-chat_panel {{ background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 8px 8px 0 {C['ink']};
                      padding: 0 16px 14px; gap: 10px; }}
.chat-head {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
              margin: 0 -16px; padding: 12px 16px; border-bottom: 3px solid {C['ink']}; }}
.st-key-chat_log {{ margin-top: 18px; background: {C['chat_bg']}; border: 3px solid {C['ink']} !important; border-radius: 0 !important; }}
.msg {{ display: flex; gap: 10px; align-items: flex-start; margin: 4px 0 2px; }}
.msg.user {{ justify-content: flex-end; }}
.avatar {{ flex: none; width: 42px; height: 42px; border: 3px solid {C['ink']}; background: {C['chip']};
           display: flex; align-items: center; justify-content: center; }}
.bubble {{ border: 3px solid {C['ink']}; box-shadow: 4px 4px 0 {C['ink']}; padding: 10px 14px;
           max-width: 78%; white-space: pre-line; line-height: 1.5; font-size: 16px; }}
.bubble.bot {{ background: {C['card']}; color: {C['ink']}; }}
.bubble.user {{ background: {C['teal']}; color: {C['btn_text']}; }}
.bubble .alert {{ display: block; background: {C['bad']}; color: #fff; padding: 6px 8px; margin: 2px 0 8px; font-weight: 800; }}
.who {{ display: block; font-family: 'Silkscreen', monospace; font-size: 10px; letter-spacing: 2px; margin-bottom: 3px; opacity: .85; }}
.st-key-chat_log .stButton > button {{ min-height: 34px; padding: 2px 12px; margin-left: 52px; box-shadow: 3px 3px 0 {C['ink']}; font-size: 14px; }}
.st-key-chat_log [class*="st-key-chip_"] button {{ margin-left: 0 !important; min-height: 32px; font-size: 13px; width: 100%; }}
.st-key-chat_log [class*="st-key-chatquiz_"] button {{ background: {C['coral']} !important; color: #1C2B33 !important; }}
.st-key-chat_panel [data-testid="InputInstructions"] {{ display: none; }}
.st-key-chat_panel .stTextInput input {{ min-height: 48px; padding: 10px 14px; }}
.st-key-chat_panel .stFormSubmitButton > button,
.st-key-chat_panel [data-testid="stPopover"] button {{ min-height: 54px; }}
[data-testid="stPopover"] button {{ font-size: 24px; padding: 0; justify-content: center; }}
[data-testid="stPopover"] button p {{ font-size: 24px; font-weight: 700; }}
[data-testid="stPopover"] button [data-testid="stIconMaterial"] {{ display: none; }}
[data-testid="stPopoverBody"] {{ background: {C['card']}; border: 3px solid {C['ink']}; border-radius: 0; }}

/* Big VIDEO and QUIZ buttons on the main page */
.st-key-open_video button, .st-key-open_quiz button {{
  height: 230px; width: 100%; flex-direction: column; gap: 14px; background: {C['card']} !important;
  border: 4px solid {C['ink']} !important; box-shadow: 8px 8px 0 {C['ink']};
  font-family: 'Silkscreen', monospace; font-size: 26px; letter-spacing: 3px;
}}
.st-key-open_video button::before, .st-key-open_quiz button::before {{
  content: ""; display: block; width: 120px; height: 90px; background-repeat: no-repeat; background-position: center;
  background-size: contain; image-rendering: pixelated;
}}
.st-key-open_video button::before {{ background-image: {play_icon}; }}
.st-key-open_quiz button::before {{ background-image: {quiz_icon}; height: 70px; width: 130px; }}
.st-key-open_video button:hover, .st-key-open_quiz button:hover {{
  transform: translate(-3px, -3px); box-shadow: 11px 11px 0 {C['coral']}; }}
.st-key-open_video button p, .st-key-open_quiz button p {{ font-size: 26px; color: {C['ink']} !important; }}

/* Tiles (fields, topics, videos) */
[class*="st-key-tile_"], [class*="st-key-tiledone_"] {{
  background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 6px 6px 0 {C['ink']};
  padding: 14px 14px 16px; gap: 10px; margin-bottom: 14px;
}}
[class*="st-key-tiledone_"] {{ background: {C['done_bg']}; border-color: {C['done_line']}; box-shadow: 6px 6px 0 {C['done_line']}; }}
.tile-title {{ font-family: 'Silkscreen', monospace; font-weight: 700; font-size: 16px; letter-spacing: 1px;
               color: {C['teal']}; text-align: center; line-height: 1.35; min-height: 44px;
               display: flex; align-items: center; justify-content: center; margin: 0; }}
.tile-count {{ display: block; text-align: center; color: {C['sub']}; font-weight: 700; font-size: 15px; }}
[class*="st-key-tiledone_"] .tile-title, [class*="st-key-tiledone_"] .tile-count {{ color: {C['done_ink']}; }}
.mini {{ height: 12px; border: 2px solid {C['ink']}; background: {C['card']}; margin: 6px 0; }}
.mini i {{ display: block; height: 100%; background: {C['coral']}; }}
.thumb {{ position: relative; display: block; width: 100%; aspect-ratio: 16/9; overflow: hidden;
          background: {C['chip']}; border: 3px solid {C['ink']}; }}
.thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.thumb b {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 28px; background: rgba(27,42,53,.28); }}
.thumb .seen {{ position: absolute; top: 6px; right: 6px; inset: auto 6px auto auto; font-size: 11px; padding: 2px 6px; }}

/* Quiz answers */
[class*="st-key-opt_"] button, [class*="st-key-optok_"] button,
[class*="st-key-optbad_"] button, [class*="st-key-optdim_"] button {{
  justify-content: flex-start; text-align: left; min-height: 56px; padding: 10px 16px; }}
[class*="st-key-opt_"] button p, [class*="st-key-optok_"] button p,
[class*="st-key-optbad_"] button p, [class*="st-key-optdim_"] button p {{ font-size: 17px; font-weight: 800; text-align: left; }}
[class*="st-key-optok_"] button {{ background: {C['ok']} !important; color: #fff !important; animation: pop .5s ease-out; }}
[class*="st-key-optbad_"] button {{ background: {C['bad']} !important; color: #fff !important; animation: shake .45s ease-in-out; }}
[class*="st-key-optdim_"] button {{ opacity: .55; }}
@keyframes pop {{ 0% {{ transform: scale(1); }} 40% {{ transform: scale(1.04) translateY(-4px); }} 100% {{ transform: scale(1); }} }}
@keyframes shake {{ 0%,100% {{ transform: translateX(0); }} 25% {{ transform: translateX(-7px); }} 50% {{ transform: translateX(7px); }} 75% {{ transform: translateX(-4px); }} }}

/* Quiz result */
.result {{ text-align: center; margin-top: 10px; }}
.result-score {{ font-family: 'Silkscreen', monospace; font-size: 18px; letter-spacing: 2px; color: {C['sub']}; margin: 14px 0 6px; }}
.result-msg {{ font-family: 'Silkscreen', monospace; font-size: 30px; letter-spacing: 2px; line-height: 1.4; margin: 0 0 18px; }}
.result-msg.win {{ color: {C['teal']}; }}
.hop {{ display: inline-block; animation: hop 1s ease-in-out infinite; }}
@keyframes hop {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}

/* Video player */
.video-screen {{ aspect-ratio: 16/9; background: #1C2B33; border: 4px solid {C['ink']};
                 display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 12px; }}
.vframe {{ width: 100%; aspect-ratio: 16/9; background: #000; border: 4px solid {C['ink']}; box-shadow: 6px 6px 0 {C['ink']}; }}
.vframe iframe {{ width: 100%; height: 100%; border: 0; display: block; }}
.vhint {{ font-size: 14px; color: {C['sub']}; margin: 10px 0 0; }}
.vhint a {{ color: {C['teal']}; font-weight: 800; }}

.tv-footer {{ display: flex; justify-content: space-between; align-items: center;
              margin: 40px -30px -30px; padding: 22px 36px; background: {C['frame']}; }}
.grille span {{ display: inline-block; width: 8px; height: 36px; margin-right: 8px; border-radius: 3px; background: {C['frame_edge']}; }}
.knob {{ display: inline-block; width: 40px; height: 40px; border-radius: 50%; background: {C['frame_edge']}; margin-left: 14px; }}
.led {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%; background: {C['coral']}; margin-left: 14px; }}
.disclaimer {{ text-align: center; font-size: 14px; color: {C['sub']}; margin-top: 18px; }}

@media (prefers-reduced-motion: reduce) {{
  * {{ animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 9. Shared pieces
# ---------------------------------------------------------------------------
def level_info():
    level = 1 + S.xp // 10
    return f"LEVEL {level} · HEALTH HERO · {S.xp} XP", (S.xp % 10) * 10


def bar_html(label, pct):
    return (f"<div class='bar-label'>{esc(label)}</div>"
            f"<div class='score-bar'><div class='score-fill' style='width:{round(pct)}%'></div></div>")


def top_bar(bar=None):
    """Logo (+ HOME), a level/score bar in the middle and the theme switch."""
    left, mid, right = st.columns([2.4, 2, 1.6], vertical_alignment="center")
    with left:
        if S.page != "home":
            home, logo = st.columns([1, 2.6], vertical_alignment="center")
            home.button("◂ HOME", on_click=go, args=("home",), key=f"home_{S.page}")
        else:
            logo = st.container()
        logo.markdown(f"<div class='logo'>{LOGO_SVG.format(w=58, h=51)}"
                      f"<span class='pixel' style='font-size:28px;letter-spacing:4px'>AIJAGA</span></div>",
                      unsafe_allow_html=True)
    with mid:
        label, pct = bar if bar else level_info()
        st.markdown(bar_html(label, pct), unsafe_allow_html=True)
    with right:
        b, d = st.columns(2)
        b.button("BRIGHT", key=f"bright_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "bright" else "secondary", on_click=set_theme, args=("bright",))
        d.button("DARK", key=f"dark_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "dark" else "secondary", on_click=set_theme, args=("dark",))


def page_heading(title, sub=None):
    st.markdown(f"<h1 class='page-title'>{esc(title)}</h1>"
                + (f"<p class='page-sub'>{esc(sub)}</p>" if sub else ""), unsafe_allow_html=True)


def tv_footer():
    st.markdown(f"<p class='disclaimer'>{DISCLAIMER}</p>"
                "<div class='tv-footer'>"
                "<div class='grille'><span></span><span></span><span></span><span></span><span></span></div>"
                f"<span class='pixel' style='color:{C['frame_text']};font-size:20px;letter-spacing:4px'>AIJAGA TV</span>"
                "<div><span class='knob'></span><span class='knob'></span><span class='led'></span></div>"
                "</div>", unsafe_allow_html=True)


def speak_if_needed():
    """Read text aloud in the browser using its built-in speech voice."""
    if S.speak:
        spoken_text = json.dumps(S.speak).replace("<", r"\u003c")
        components.html(
            "<script>try{const s=window.parent.speechSynthesis||window.speechSynthesis;"
            f"s.cancel();s.speak(new SpeechSynthesisUtterance({spoken_text}));}}catch(e){{}}</script>",
            height=0)
        S.speak = None


CONFETTI_JS = r"""
(function(){
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var old = document.getElementById('aijaga-confetti'); if (old) old.remove();
  var cv = document.createElement('canvas'); cv.id = 'aijaga-confetti';
  cv.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:999999';
  cv.width = window.innerWidth; cv.height = window.innerHeight; document.body.appendChild(cv);
  var ctx = cv.getContext('2d');
  var colors = ['#e07050','#2d6a5a','#f2c14e','#4aa3df','#ffffff','#f08a68','#7bd389'];
  var parts = [];
  function spawn(n){ for (var k=0;k<n;k++) parts.push({x:Math.random()*cv.width, y:-20-Math.random()*120,
    s:6+Math.floor(Math.random()*7), vy:1.8+Math.random()*2.6, vx:-1+Math.random()*2,
    c:colors[Math.floor(Math.random()*colors.length)], ph:Math.random()*Math.PI*2}); }
  spawn(110);
  var start = performance.now();
  function frame(t){
    ctx.clearRect(0,0,cv.width,cv.height);
    if (t-start < 4500 && parts.length < 260) spawn(2);
    for (var i=parts.length-1;i>=0;i--){ var p=parts[i];
      p.y+=p.vy; p.x+=p.vx+Math.sin(p.y/28+p.ph)*0.8;
      ctx.fillStyle=p.c; ctx.fillRect(Math.round(p.x),Math.round(p.y),p.s,p.s);
      if (p.y>cv.height+20) parts.splice(i,1); }
    if ((parts.length || t-start < 4500) && t-start < 12000) requestAnimationFrame(frame); else cv.remove();
  }
  requestAnimationFrame(frame);
})();
"""


def confetti():
    """Pixel confetti over the whole app (runs in the main page, falls back to balloons)."""
    code = json.dumps(CONFETTI_JS).replace("<", r"\u003c")
    components.html(
        "<script>try{const d=window.parent.document;const s=d.createElement('script');"
        f"s.textContent={code};d.body.appendChild(s);s.remove();}}catch(e){{}}</script>",
        height=0)


# ---------------------------------------------------------------------------
# 10. Quiz logic
# ---------------------------------------------------------------------------
def qkey(fi, qi):
    return FIELDS[fi]["name"] + "|" + FIELDS[fi]["quizzes"][qi]["title"]


def total_of(fi, qi):
    return min(Q_PER, len(FIELDS[fi]["quizzes"][qi]["questions"]))


def get_status(fi, qi):
    total = total_of(fi, qi)
    p = S.progress.get(qkey(fi, qi))
    answered = max(0, min(total, p["answered"])) if p else 0
    score = max(0, min(answered, p["score"])) if p else 0
    if answered == 0:
        return {"kind": "new", "total": total}
    if answered >= total:
        return {"kind": "done", "answered": answered, "score": score, "total": total}
    return {"kind": "part", "answered": answered, "score": score, "total": total,
            "pct": round(answered / total * 100), "left": total - answered}


def start_quiz(fi, qi):
    """Unfinished quiz -> continue where you stopped. New or finished -> fresh attempt."""
    items = []
    for q in FIELDS[fi]["quizzes"][qi]["questions"][:Q_PER]:
        opts = list(dict.fromkeys(q["options"]))  # remove duplicate options
        random.shuffle(opts)
        items.append({"q": q["q"], "answer": q["answer"], "opts": opts})
    status = get_status(fi, qi)
    resume = status["kind"] == "part"
    S.update(q_field=fi, q_topic=qi, q_items=items, q_pick=None, celebrate=False,
             q_i=status["answered"] if resume else 0, q_score=status["score"] if resume else 0,
             page="quiz_play")


def choose_answer(k):
    if S.q_pick is not None:
        return
    S.q_pick = k
    item = S.q_items[S.q_i]
    if item["opts"][k] == item["answer"]:
        S.q_score += 1
        S.xp += 1
    # save right away, so leaving mid-quiz keeps the progress
    S.progress[qkey(S.q_field, S.q_topic)] = {"answered": S.q_i + 1, "score": S.q_score}


def next_question():
    S.q_pick = None
    S.q_i += 1
    if S.q_i >= len(S.q_items):
        S.page = "quiz_result"
        S.celebrate = S.q_score >= len(S.q_items) - 1


# ---------------------------------------------------------------------------
# 11. Chat helpers
# ---------------------------------------------------------------------------
def bot_reply(text, **extra):
    S.messages.append({"role": "bot", "text": text, **extra})
    if S.read_aloud:
        S.speak = text


def call_agnes(question, key):
    """Returns (reply, error_message)."""
    history = [{"role": "assistant" if m["role"] == "bot" else "user", "content": m["text"]}
               for m in S.messages if m.get("agnes_turn")][-20:]
    payload = {"model": "agnes-2.5-flash", "messages": [
        {"role": "system", "content": CHAT_INSTRUCTIONS}, *history,
        {"role": "user", "content": question}]}
    request = Request("https://apihub.agnes-ai.com/v1/chat/completions",
                      data=json.dumps(payload).encode(),
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with st.spinner("Dr. Azmi is replying..."), urlopen(request, timeout=45) as response:
            reply = json.load(response)["choices"][0]["message"]["content"]
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("Empty reply")
            return reply.strip(), None
    except HTTPError as exc:
        if exc.code in (401, 403):
            return None, "Check your Agnes API key and model access."
        if exc.code == 429:
            return None, "Agnes AI's usage limit was reached."
        return None, f"Agnes AI returned HTTP {exc.code}."
    except (OSError, URLError, ValueError, KeyError, IndexError, TypeError):
        return None, "Could not get a reply from Agnes AI."


def ask(question):
    question = (question or "").strip()
    if not question:
        return
    S.chat_error = None
    hit = find_topic(question)
    emergency = bool(EMERGENCY.search(question))

    try:
        key = st.secrets["AGNES_API_KEY"].strip()
    except Exception:  # no secrets file, or key missing
        key = ""

    reply, chips, used_ai = None, [], False
    if key:
        reply, err = call_agnes(question, key)
        if reply:
            used_ai = True
            S.chat_note = None
        else:
            S.chat_error = err + " Dr. Azmi answered from the AiJaga topic library instead."
    else:
        S.chat_note = "Offline mode: answers come from the AiJaga topic library."
    if not reply:
        reply, chips = library_reply(question, hit, emergency)

    S.messages.append({"role": "user", "text": question, "agnes_turn": used_ai})
    bot_reply(reply, agnes_turn=used_ai, alert=emergency, chips=chips,
              quiz=[hit["fi"], hit["qi"]] if hit else None)


def chat_box():
    with st.container(key="chat_panel"):
        st.markdown("<div class='chat-head'>"
                    "<span class='pixel' style='font-size:15px'>CHAT WITH DR. AZMI</span>"
                    "<span class='pixel sub' style='font-size:12px'>"
                    f"<span style='display:inline-block;width:10px;height:10px;background:{C['online']};margin-right:8px'></span>"
                    "AI ASSISTANT</span></div>", unsafe_allow_html=True)
        if S.chat_error:
            st.warning(S.chat_error)
        elif S.chat_note:
            st.caption(S.chat_note)

        # Message history (scrolls when it gets long)
        with st.container(height=360, key="chat_log"):
            for i, msg in enumerate(S.messages):
                text = esc(msg["text"])
                if msg["role"] == "bot":
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    reply = "<br>".join("• " + line[2:] if line.startswith(("- ", "* ")) else line
                                         for line in lines)
                    alert = f"<span class='alert'>⚠ {EMERGENCY_NOTE}</span>" if msg.get("alert") else ""
                    st.html(f"<div class='msg'><div class='avatar'>{MINI_DOCTOR_SVG}</div>"
                            f"<div class='bubble bot'><span class='who'>DR. AZMI</span>{alert}{reply}</div></div>")
                    st.button("🔊 Listen", key=f"listen_{i}", on_click=lambda t=msg["text"]: S.update(speak=t))
                    if msg.get("quiz"):
                        fi, qi = msg["quiz"]
                        st.button(f"? TAKE THE QUIZ: {FIELDS[fi]['quizzes'][qi]['title']}", key=f"chatquiz_{i}",
                                  on_click=start_quiz, args=(fi, qi))
                    if msg.get("chips"):
                        cols = st.columns(len(msg["chips"]))
                        for k, (col, title) in enumerate(zip(cols, msg["chips"])):
                            col.button(title, key=f"chip_{i}_{k}", on_click=ask, args=(title,))
                else:
                    if msg.get("image") is not None:
                        _, img = st.columns([2, 1])
                        img.image(msg["image"], use_container_width=True)
                    st.markdown(f"<div class='msg user'><div class='bubble user'>"
                                f"<span class='who'>YOU</span>{text}</div></div>", unsafe_allow_html=True)

        # "+" attach button, typing box and SEND
        plus, rest = st.columns([1, 9], vertical_alignment="bottom")
        with plus.popover("+", help="Add a photo or voice note", use_container_width=True):
            photo = st.file_uploader("Send a photo", type=["png", "jpg", "jpeg"], key="photo")
            if photo is not None and st.button("Send photo", key="send_photo", type="primary"):
                S.messages.append({"role": "user", "text": "(Photo sent)", "image": photo.getvalue()})
                bot_reply("Thanks for the photo! Photo checking is coming soon. "
                          "For now, please also describe what you see in words.")
                st.rerun()
            voice = st.audio_input("Record a voice note", key="voice")
            if voice is not None and st.button("Send voice note", key="send_voice", type="primary"):
                S.messages.append({"role": "user", "text": "(Voice note sent)"})
                bot_reply("Thanks for the voice note! Voice support is coming soon. "
                          "For now, please type your question.")
                st.rerun()
            st.checkbox("Read Dr. Azmi's replies aloud", value=S.read_aloud, key="read_aloud_box",
                        on_change=lambda: S.update(read_aloud=S.read_aloud_box))
        with rest:
            with st.form("ask_form", clear_on_submit=True, border=False):
                box, send = st.columns([5, 1], vertical_alignment="bottom")
                question = box.text_input("Your healthcare question", label_visibility="collapsed",
                                          max_chars=500, placeholder="Type your healthcare question here...")
                if send.form_submit_button("SEND", use_container_width=True):
                    ask(question)
                    st.rerun()


# ---------------------------------------------------------------------------
# 12. Pages
# ---------------------------------------------------------------------------
def home_page():
    top_bar()
    main, side = st.columns([2.3, 1], gap="large")

    with main:
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:34px;margin:18px 0 26px'>"
            f"<div style='text-align:center'>{DOCTOR_SVG.format(w=88, h=110)}<br><span class='tag'>DR. AZMI</span></div>"
            "<div class='bubble-hello'>"
            "<div class='pixel sub' style='font-size:12px'>DR. AZMI</div>"
            "<p style='font-size:20px;font-weight:700;margin:6px 0 8px'>Hi, I am Dr. Azmi!</p>"
            "<p style='font-size:16px;margin:0 0 10px'>Ask me a health question below, or press "
            "<b>Video</b> or <b>Quiz</b> to learn and play.</p>"
            "<div class='dots' aria-hidden='true'><span></span><span></span><span></span></div>"
            "</div></div>", unsafe_allow_html=True)
        chat_box()

    with side:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.button("VIDEO", key="open_video", on_click=go, args=("video_fields",), use_container_width=True,
                  help="Watch short health and first-aid videos")
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        st.button("QUIZ", key="open_quiz", on_click=go, args=("quiz_fields",), use_container_width=True,
                  help="Test your health knowledge")

    speak_if_needed()
    tv_footer()


def tile_grid(n, per_row=3):
    """Yields (index, column) for a grid of tiles."""
    cols = None
    for i in range(n):
        if i % per_row == 0:
            cols = st.columns(per_row, gap="medium")
        yield i, cols[i % per_row]


# ---- QUIZ ----------------------------------------------------------------
def quiz_fields_page():
    top_bar()
    page_heading("( ? ) PICK A FIELD", "WHAT DO YOU WANT TO BE QUIZZED ON?")
    for fi, col in tile_grid(len(FIELDS)):
        f = FIELDS[fi]
        statuses = [get_status(fi, qi)["kind"] for qi in range(len(f["quizzes"]))]
        done, part = statuses.count("done"), statuses.count("part")
        all_done = done == len(f["quizzes"])
        count = f"{done}/{len(f['quizzes'])} done" + (f" · {part} in progress" if part else "")
        with col, st.container(key=f"{'tiledone' if all_done else 'tile'}_qf{fi}"):
            st.markdown(f"<p class='tile-title'>{esc(f['name'].upper())}</p>"
                        f"<span class='tile-count'>{count}</span>", unsafe_allow_html=True)
            st.button("OPEN ▸", key=f"qf_{fi}", use_container_width=True,
                      on_click=lambda fi=fi: S.update(q_field=fi, page="quiz_topics"))
    tv_footer()


def quiz_topics_page():
    fi = S.q_field
    f = FIELDS[fi]
    top_bar()
    page_heading(f["name"].upper(), "PICK A TOPIC")
    for qi, col in tile_grid(len(f["quizzes"])):
        z = f["quizzes"][qi]
        s = get_status(fi, qi)
        if s["kind"] == "done":
            body = f"<span class='tile-count'>✓ DONE · {s['score']}/{s['total']}</span>"
            label, kind = "PLAY AGAIN", "secondary"
        elif s["kind"] == "part":
            body = (f"<div class='mini'><i style='width:{s['pct']}%'></i></div>"
                    f"<span class='tile-count'>{s['pct']}% done · {s['left']} left</span>")
            label, kind = "CONTINUE ▸", "primary"
        else:
            body = f"<span class='tile-count'>{s['total']} questions</span>"
            label, kind = "START ▸", "secondary"
        with col, st.container(key=f"{'tiledone' if s['kind'] == 'done' else 'tile'}_qt{fi}_{qi}"):
            st.markdown(f"<p class='tile-title'>{esc(z['title'].upper())}</p>{body}", unsafe_allow_html=True)
            st.button(label, key=f"qt_{fi}_{qi}", type=kind, use_container_width=True,
                      on_click=start_quiz, args=(fi, qi))
    _, mid, _ = st.columns([1, 1, 1])
    mid.button("◂ BACK TO FIELDS", use_container_width=True, on_click=go, args=("quiz_fields",))
    tv_footer()


def quiz_play_page():
    if not S.q_items:
        S.page = "quiz_fields"
        st.rerun()
    total = len(S.q_items)
    i, pick = S.q_i, S.q_pick
    answered = pick is not None
    item = S.q_items[i]
    title = FIELDS[S.q_field]["quizzes"][S.q_topic]["title"]

    top_bar((f"SCORE {S.q_score} / {total} · QUESTION {i + 1} OF {total}",
             (i + (1 if answered else 0)) / total * 100))
    page_heading(f"( ? ) {title.upper()}")
    _, mid, _ = st.columns([0.6, 2, 0.6])
    with mid:
        st.markdown(f"<div class='card' style='margin-top:10px'><span class='tag'>QUESTION {i + 1} OF {total}</span>"
                    f"<p style='font-size:22px;font-weight:800;line-height:1.35;margin:14px 0 0'>{esc(item['q'])}</p></div>",
                    unsafe_allow_html=True)
        for k, option in enumerate(item["opts"]):
            prefix, label = "opt", option
            if answered:
                if option == item["answer"]:
                    prefix, label = "optok", "✓ " + option
                elif k == pick:
                    prefix, label = "optbad", "✕ " + option
                else:
                    prefix = "optdim"
            st.button(label, key=f"{prefix}_{i}_{k}", on_click=choose_answer, args=(k,), use_container_width=True)

        if answered:
            if item["opts"][pick] == item["answer"]:
                st.success("★ CORRECT! +1 XP")
            else:
                st.error(f"✕ NOT QUITE — the correct answer is: {item['answer']}")
            last = i == total - 1
            a, b = st.columns(2)
            a.button("SEE SCORE ▸" if last else "NEXT ▸", type="primary", use_container_width=True,
                     on_click=next_question)
            b.button("◂ TOPICS", use_container_width=True, on_click=go, args=("quiz_topics",))
        else:
            st.button("◂ TOPICS (progress is saved)", on_click=go, args=("quiz_topics",))
    tv_footer()


def quiz_result_page():
    total, s = len(S.q_items), S.q_score
    if s == total:
        msg, mood, win = "Congrats, you nailed it!", "happy", True
    elif s == total - 1:
        msg, mood, win = "So close!", "ok", False
    else:
        msg, mood, win = "It's okay, you can try again.", "flat", False
    celebrate = s >= total - 1

    top_bar((f"SCORE {s} / {total} · COMPLETE", 100))
    _, mid, _ = st.columns([0.6, 2, 0.6])
    with mid:
        st.markdown(f"<div class='card result'><span class='tag'>LEVEL COMPLETE!</span><br><br>"
                    f"<div class='{'hop' if celebrate else ''}'>{mood_doctor(mood, 10)}</div>"
                    f"<p class='result-score'>YOU GOT {s} / {total}</p>"
                    f"<p class='result-msg {'win' if win else ''}'>{esc(msg)}</p>"
                    f"<p class='sub' style='font-weight:700'>{esc(level_info()[0])}</p></div>",
                    unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.button("TRY AGAIN", type="primary", use_container_width=True,
                 on_click=start_quiz, args=(S.q_field, S.q_topic))
        b.button("TRY OTHER QUIZ", use_container_width=True, on_click=go, args=("quiz_fields",))
        c.button("ASK DR. AZMI", use_container_width=True, on_click=go, args=("home",))
    if S.celebrate:
        S.celebrate = False
        confetti()
    tv_footer()


# ---- VIDEO ---------------------------------------------------------------
def thumb_html(v):
    seen = "<span class='tag seen'>✓ WATCHED</span>" if v["id"] in S.video_seen else ""
    return (f"<span class='thumb'><img src='https://i.ytimg.com/vi/{quote(v['id'])}/mqdefault.jpg' alt='' "
            f"loading='lazy'><b>▶</b>{seen}</span>")


def video_fields_page():
    top_bar()
    page_heading("▶ PICK A FIELD", "WHAT DO YOU WANT TO WATCH?")
    for fi, col in tile_grid(len(FIELDS)):
        vids = videos_in_field(fi)
        watched = sum(v["id"] in S.video_seen for v in vids)
        pct = round(watched / len(vids) * 100) if vids else 0
        with col, st.container(key=f"tile_vf{fi}"):
            st.markdown(f"<p class='tile-title'>{esc(FIELDS[fi]['name'].upper())}</p>"
                        f"<div class='mini'><i style='width:{pct}%'></i></div>"
                        f"<span class='tile-count'>{len(vids)} videos · {watched} watched</span>",
                        unsafe_allow_html=True)
            st.button("OPEN ▸", key=f"vf_{fi}", use_container_width=True,
                      on_click=lambda fi=fi: S.update(v_field=fi, page="video_list"))
    tv_footer()


def video_list_page():
    fi = S.v_field
    vids = videos_in_field(fi)
    top_bar()
    page_heading(FIELDS[fi]["name"].upper(), "PICK A VIDEO")
    for i, col in tile_grid(len(vids)):
        v = vids[i]
        with col, st.container(key=f"tile_vl{fi}_{i}"):
            st.markdown(f"{thumb_html(v)}<p class='tile-title'>{esc(v['title'].upper())}</p>",
                        unsafe_allow_html=True)
            st.button("▶ WATCH", key=f"vl_{fi}_{i}", type="primary", use_container_width=True,
                      on_click=lambda i=i: S.update(v_i=i, page="video_watch"))
    _, mid, _ = st.columns([1, 1, 1])
    mid.button("◂ BACK TO FIELDS", use_container_width=True, on_click=go, args=("video_fields",))
    tv_footer()


def video_watch_page():
    fi = S.v_field
    vids = videos_in_field(fi)
    n = len(vids)
    S.v_i = S.v_i % n
    v = vids[S.v_i]
    S.video_seen.add(v["id"])
    qi = quiz_index(fi, v["quiz"])
    vid = quote(v["id"])
    watched = sum(x["id"] in S.video_seen for x in vids)

    def select(k):
        S.v_i = k % n

    top_bar()
    player, playlist = st.columns([2.2, 1], gap="large")

    with player:
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin:14px 0 10px'>"
                    f"<h2 style='font-size:20px;margin:0'>NOW PLAYING</h2>"
                    f"<span class='tag'>{esc(FIELDS[fi]['name'].upper())}</span></div>"
                    f"<div class='vframe'><iframe src='https://www.youtube-nocookie.com/embed/{vid}?rel=0' "
                    f"title='{esc(v['title'])}' allow='accelerometer; autoplay; clipboard-write; encrypted-media; "
                    f"picture-in-picture' allowfullscreen referrerpolicy='strict-origin-when-cross-origin'></iframe></div>"
                    f"<p style='font-size:24px;font-weight:800;margin:16px 0 0'>{esc(v['title'])}</p>"
                    f"<p class='vhint'>Video not playing? <a href='https://www.youtube.com/watch?v={vid}' "
                    f"target='_blank' rel='noopener noreferrer'>Open it on YouTube</a></p>",
                    unsafe_allow_html=True)
        a, b, c, d = st.columns(4)
        b.button("◂ PREV", use_container_width=True, on_click=select, args=(S.v_i - 1,))
        c.button("NEXT ▸", use_container_width=True, on_click=select, args=(S.v_i + 1,))
        if qi >= 0:
            a.button("TAKE THE QUIZ", type="primary", use_container_width=True, on_click=start_quiz, args=(fi, qi))
        d.button("◂ VIDEOS", use_container_width=True, on_click=go, args=("video_list",))

    with playlist:
        st.markdown(f"<h2 style='font-size:16px;margin:14px 0 4px'>PLAYLIST</h2>"
                    + bar_html(f"WATCHED {watched} OF {n}", watched / n * 100), unsafe_allow_html=True)
        for k, x in enumerate(vids):
            mark = "▶ " if k == S.v_i else ("✓ " if x["id"] in S.video_seen else "")
            st.button(f"{k + 1:02d} · {mark}{x['title']}", key=f"pl_{k}", on_click=select, args=(k,),
                      type="primary" if k == S.v_i else "secondary", use_container_width=True)
    tv_footer()


# ---------------------------------------------------------------------------
# 13. Show the right page
# ---------------------------------------------------------------------------
PAGES = {
    "home": home_page,
    "quiz_fields": quiz_fields_page,
    "quiz_topics": quiz_topics_page,
    "quiz_play": quiz_play_page,
    "quiz_result": quiz_result_page,
    "video_fields": video_fields_page,
    "video_list": video_list_page,
    "video_watch": video_watch_page,
}

inject_css()
PAGES.get(S.page, home_page)()