"""
AiJaga Health Quiz
------------------
A retro "pixel TV" quiz app.

This file holds the quiz data and the page. Run it through Streamlit:
    pip install streamlit
    streamlit run streamlit_app.py
(keep this file in the same folder as streamlit_app.py)

Flow:  Home -> Quiz -> pick a health field -> pick a title -> 3 questions -> result
"""

import json



# ----------------------------------------------------------------------------
# QUIZ DATA
# Q(question, correct_answer, wrong_1, wrong_2, wrong_3)
# Answer positions are shuffled in the browser every time a quiz starts.
# ----------------------------------------------------------------------------
def Q(question, correct, *wrong):
    return {"q": question, "answer": correct, "options": [correct, *wrong]}


FIELDS = [
    # ------------------------------------------------------------------ 1
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
    # ------------------------------------------------------------------ 2
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
    # ------------------------------------------------------------------ 3
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
    # ------------------------------------------------------------------ 4
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
    # ------------------------------------------------------------------ 5
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
    # ------------------------------------------------------------------ 6
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
    # ------------------------------------------------------------------ 7
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


# ----------------------------------------------------------------------------
# PAGE (HTML + CSS + JS, displayed by streamlit_app.py)
# ----------------------------------------------------------------------------
PAGE = r"""<!doctype html>
<html lang="en" data-theme="bright">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AiJaga - Health Quiz</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{
  --page:#fbf5ea; --frame:#ecc99a; --edge:#d9a86c; --knob:#d9a86c; --frame-ink:#8a5a2b;
  --bg:#d5e9e1; --scan:rgba(45,106,90,.07); --ink:#1b2a35; --muted:#41525d;
  --card:#ffffff; --opt:#d3e8e0; --green:#2d6a5a; --coral:#e07050;
  --ok:#2f9e6b; --bad:#d64545; --on-solid:#ffffff;
  --soft-line:rgba(27,42,53,.32); --soft-bg:rgba(255,255,255,.30);
  --done-bg:#dcdedd; --done-ink:#6a7378; --done-line:#9aa3a8;
}
:root[data-theme="dark"]{
  --page:#0b141a; --frame:#8a6a45; --edge:#6b4f31; --knob:#6b4f31; --frame-ink:#f0d9b5;
  --bg:#13222b; --scan:rgba(95,195,160,.06); --ink:#e6f0ec; --muted:#a9bcc4;
  --card:#1d313c; --opt:#27424f; --green:#5fc3a0; --coral:#f08a68;
  --ok:#2f9e6b; --bad:#d64545; --on-solid:#ffffff;
  --soft-line:rgba(230,240,236,.28); --soft-bg:rgba(255,255,255,.05);
  --done-bg:#26323a; --done-ink:#7d8b93; --done-line:#4a5861;
}
*{box-sizing:border-box}
html,body{margin:0}
body{
  background:var(--page); color:var(--ink);
  font-family:"Nunito",system-ui,sans-serif; font-weight:700;
  min-height:100vh; padding:20px 14px; display:flex; justify-content:center;
}
button,input{font:inherit; color:inherit}
:focus-visible{outline:3px solid var(--coral); outline-offset:3px}
[hidden]{display:none !important}

/* ---- TV frame ---- */
.tv{
  width:100%; max-width:980px; background:var(--frame);
  border-radius:38px; padding:16px 16px 10px; border:4px solid var(--edge);
  box-shadow:0 6px 0 var(--edge); align-self:flex-start;
}
.screen{
  position:relative; overflow:hidden; border-radius:24px; border:4px solid var(--edge);
  background:repeating-linear-gradient(0deg, var(--scan) 0 2px, transparent 2px 5px), var(--bg);
  min-height:600px; padding:18px 20px 14px; display:flex; flex-direction:column;
}
.tv-base{display:grid; grid-template-columns:1fr auto 1fr; align-items:center; padding:14px 18px 8px}
.tv-base .grille{display:flex; gap:6px}
.tv-base .grille i{display:block; width:5px; height:26px; background:var(--edge); border-radius:2px}
.tv-base .name{font-family:"Press Start 2P",monospace; font-size:10px; letter-spacing:3px; color:var(--frame-ink)}
.tv-base .knobs{display:flex; gap:12px; justify-content:flex-end; align-items:center}
.tv-base .knobs i{display:block; width:30px; height:30px; border-radius:50%; background:var(--knob)}
.tv-base .knobs i.dot{width:10px; height:10px; background:var(--coral)}

/* ---- header ---- */
.hdr{display:grid; grid-template-columns:auto 1fr auto; gap:16px; align-items:center}
.hdr-left{display:flex; align-items:center; gap:10px; min-height:40px}
.logo{display:flex; align-items:center; gap:10px; font-family:"Press Start 2P",monospace; font-size:14px; color:var(--green); letter-spacing:2px}
.logo b{display:block; width:24px; height:24px; background:var(--green); border:3px solid var(--coral)}
.hdr-mid{min-width:0; max-width:340px; width:100%; justify-self:center}
.tiny{display:block; font-family:"Press Start 2P",monospace; font-size:8px; letter-spacing:1.5px; color:var(--muted); margin-bottom:6px; text-align:left; line-height:1.5}
.bar{height:14px; background:var(--card); border:3px solid var(--ink)}
.bar i{display:block; height:100%; width:0; background:var(--coral); transition:width .6s cubic-bezier(.3,.8,.3,1)}
.hdr-right{display:flex; gap:8px}

.btn{
  font-family:"Press Start 2P",monospace; font-size:9px; letter-spacing:1px;
  padding:11px 12px; background:var(--card); border:3px solid var(--ink); color:var(--ink);
  cursor:pointer; box-shadow:3px 3px 0 var(--ink); transition:transform .08s, box-shadow .08s;
}
.btn:hover{transform:translate(-1px,-1px); box-shadow:4px 4px 0 var(--ink)}
.btn:active{transform:translate(2px,2px); box-shadow:1px 1px 0 var(--ink)}
.btn.on{background:var(--green); color:var(--on-solid)}
.btn.big{font-size:11px; padding:16px 20px; background:var(--green); color:var(--on-solid)}
.btn.big.alt{background:var(--card); color:var(--ink)}
.btn.small{padding:10px 12px; font-size:8px}
:root[data-theme="dark"] .btn.on,
:root[data-theme="dark"] .btn.big{color:#0b141a}
:root[data-theme="dark"] .btn.big.alt{color:var(--ink)}

/* ---- stage + generic ---- */
#stage{flex:1; display:flex; flex-direction:column; align-items:center; padding:20px 0 10px}
.title{
  font-family:"Press Start 2P",monospace; font-size:clamp(15px,3vw,26px); color:var(--ink);
  letter-spacing:3px; margin:6px 0 22px; text-align:center; line-height:1.5;
}
.sub{font-family:"Press Start 2P",monospace; font-size:10px; letter-spacing:3px; color:var(--ink); margin:-8px 0 22px; text-align:center; line-height:1.6}

/* ---- HOME ---- */
.home{width:100%; display:flex; flex-direction:column; align-items:center; gap:14px}
.mascot{display:flex; flex-direction:column; align-items:center; gap:8px}
.bob svg{animation:bob 1.6s steps(1) infinite}
@keyframes bob{0%,49%{transform:translateY(0)} 50%,100%{transform:translateY(-4px)}}
.tag{background:var(--coral); color:#fff; font-family:"Press Start 2P",monospace; font-size:8px; letter-spacing:2px; padding:7px 11px; border:3px solid var(--ink)}
:root[data-theme="dark"] .tag{color:#0b141a}
.hello{font-family:"Press Start 2P",monospace; font-size:clamp(11px,2.3vw,17px); letter-spacing:2px; color:var(--green); text-align:center; line-height:1.7; margin:2px 0 0}
.hello-sub{margin:-4px 0 0; font-size:15px; color:var(--muted); text-align:center}

/* chat zone: fixed size, so nothing jumps when it swaps between START and chat */
.chat-zone{position:relative; width:100%; max-width:700px; height:250px}
.chat-start{
  position:absolute; inset:0; width:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px;
  background:var(--green); color:#fff; border:4px solid var(--ink); box-shadow:6px 6px 0 var(--ink);
  cursor:pointer; opacity:1; transition:opacity .18s;
}
:root[data-theme="dark"] .chat-start{color:#0b141a}
.chat-start .go{display:flex; align-items:center; gap:18px; font-family:"Press Start 2P",monospace; font-size:clamp(20px,4vw,30px); letter-spacing:6px}
.chat-start .hint{font-size:14px; font-weight:800; opacity:.92}
.chat-zone.open .chat-start{opacity:0; visibility:hidden; transition:opacity .18s, visibility 0s .18s}
.chat-panel{
  position:absolute; inset:0; display:flex; flex-direction:column; overflow:hidden;
  background:var(--card); border:4px solid var(--ink); box-shadow:6px 6px 0 var(--ink);
  opacity:0; visibility:hidden; transition:opacity .18s, visibility 0s .18s;
}
.chat-zone.open .chat-panel{opacity:1; visibility:visible; transition:opacity .18s}
.msgs{flex:1; overflow-y:auto; padding:10px 12px; display:flex; flex-direction:column; gap:8px}
.msg{max-width:90%; padding:8px 11px; border:2px solid var(--ink); font-size:14px; line-height:1.4; font-weight:700}
.msg.bot{background:var(--opt); align-self:flex-start}
.msg.me{background:var(--green); color:#fff; align-self:flex-end}
:root[data-theme="dark"] .msg.me{color:#0b141a}
.msg ul{margin:6px 0 4px; padding-left:18px}
.msg li{margin:0 0 5px}
.msg .fq{display:block; font-size:12px; color:var(--muted); font-weight:700}
.msg .fine{display:block; margin-top:6px; font-size:11px; color:var(--muted); font-weight:600}
.msg .alert{background:var(--bad); color:#fff; padding:6px 8px; margin-bottom:6px; font-weight:800}
.chips{display:flex; flex-wrap:wrap; gap:6px; margin-top:6px}
.chip{
  font-size:12px; font-weight:800; padding:5px 9px; background:var(--card); color:var(--ink);
  border:2px solid var(--ink); cursor:pointer; box-shadow:2px 2px 0 var(--ink);
}
.chip:hover{transform:translate(-1px,-1px)}
.chip.go{background:var(--coral); color:#fff}
:root[data-theme="dark"] .chip.go{color:#0b141a}
.chat-in{display:flex; gap:8px; padding:10px; border-top:3px solid var(--ink); background:var(--opt)}
.chat-in input{
  flex:1; min-width:0; padding:10px 12px; font-size:16px; font-weight:700;
  background:var(--card); color:var(--ink); border:3px solid var(--ink);
}
.chat-in input::placeholder{color:var(--muted); font-weight:600}

/* other modes: quiet on purpose */
.modes{display:flex; gap:14px; width:100%; max-width:700px; justify-content:center}
.mode{
  flex:1; display:flex; align-items:center; justify-content:center; gap:12px; padding:13px 14px;
  background:var(--soft-bg); border:3px solid var(--soft-line); color:var(--muted); cursor:pointer;
  font-family:"Press Start 2P",monospace; font-size:10px; letter-spacing:2px; transition:border-color .12s, color .12s, background .12s;
}
.mode:hover{border-color:var(--ink); color:var(--ink); background:var(--card)}
.mode .qmark{font-size:14px; letter-spacing:3px}

/* ---- tiles (fields + topics) ---- */
.grid{display:grid; gap:20px; width:100%; max-width:760px; grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.tile{
  text-align:center; background:var(--card); color:var(--ink); border:4px solid var(--ink);
  box-shadow:5px 5px 0 var(--ink); padding:20px 14px 18px; cursor:pointer;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px;
  transition:transform .1s, box-shadow .1s;
}
.tile:hover{transform:translate(-2px,-2px); box-shadow:7px 7px 0 var(--ink)}
.tile:active{transform:translate(3px,3px); box-shadow:2px 2px 0 var(--ink)}
.tile h3{margin:0; font-family:"Press Start 2P",monospace; font-size:10px; letter-spacing:2px; color:var(--green); line-height:1.7}
.tile .count{font-size:13px; color:var(--muted)}
.mini{width:100%; height:10px; border:2px solid var(--ink); background:var(--card)}
.mini i{display:block; height:100%; background:var(--coral)}
.badge{font-family:"Press Start 2P",monospace; font-size:7px; letter-spacing:1px; background:var(--coral); color:#fff; padding:5px 7px; border:2px solid var(--ink)}
:root[data-theme="dark"] .badge{color:#0b141a}
.tile.part .count{color:var(--ink)}
.tile.done{background:var(--done-bg); border-color:var(--done-line); box-shadow:5px 5px 0 var(--done-line)}
.tile.done h3, .tile.done .count{color:var(--done-ink)}
.tile.done:hover{box-shadow:7px 7px 0 var(--done-line)}
.actions{display:flex; gap:16px; flex-wrap:wrap; justify-content:center; margin-top:18px}

/* ---- quiz ---- */
.qcard{position:relative; width:100%; max-width:560px; margin-top:10px}
.qtag{
  position:absolute; left:-4px; top:-18px; background:var(--coral); color:#fff; border:3px solid var(--ink);
  font-family:"Press Start 2P",monospace; font-size:8px; letter-spacing:2px; padding:8px 12px;
}
:root[data-theme="dark"] .qtag{color:#0b141a}
.qbox{background:var(--card); border:4px solid var(--ink); box-shadow:6px 6px 0 var(--ink); padding:34px 26px 26px}
.qtext{margin:0 0 20px; font-size:21px; line-height:1.35; font-weight:800}
.opts{display:grid; gap:12px}
.opt{
  width:100%; text-align:left; padding:15px 16px; font-size:17px; font-weight:800; cursor:pointer;
  background:var(--opt); color:var(--ink); border:3px solid var(--ink); box-shadow:3px 3px 0 var(--ink);
  transition:transform .08s, box-shadow .08s, background .15s;
}
.opts:not(.locked) .opt:hover{transform:translate(-1px,-1px); box-shadow:4px 4px 0 var(--ink)}
.opts.locked .opt{cursor:default}
.opt.ok{background:var(--ok); color:var(--on-solid); animation:pop .5s ease-out}
.opt.bad{background:var(--bad); color:var(--on-solid); animation:shake .45s ease-in-out}
.opt.dim{opacity:.55}
.feedback{min-height:24px; margin:16px 0 0; font-size:16px; font-weight:800}
.feedback.ok{color:var(--ok)} .feedback.bad{color:var(--bad)}
@keyframes pop{0%{transform:scale(1)} 40%{transform:scale(1.07) translateY(-5px)} 70%{transform:scale(.98)} 100%{transform:scale(1)}}
@keyframes shake{0%,100%{transform:translateX(0)} 20%{transform:translateX(-7px)} 40%{transform:translateX(7px)} 60%{transform:translateX(-5px)} 80%{transform:translateX(5px)}}

/* ---- result ---- */
.result{display:flex; flex-direction:column; align-items:center; gap:14px; text-align:center; width:100%}
.result .score{font-family:"Press Start 2P",monospace; font-size:12px; letter-spacing:2px; color:var(--muted)}
.result .msg2{font-family:"Press Start 2P",monospace; font-size:clamp(14px,3vw,24px); line-height:1.6; letter-spacing:2px; max-width:640px}
.result .msg2.win{color:var(--green)}
.hop{animation:hop 1s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)}}

#confetti{position:absolute; inset:0; width:100%; height:100%; pointer-events:none; z-index:5}
.note{text-align:center; font-size:12px; color:var(--muted); margin:10px 0 0; font-weight:600}
.toast{
  position:absolute; left:50%; bottom:56px; transform:translateX(-50%); z-index:6;
  background:var(--ink); color:var(--bg); padding:12px 16px; font-size:14px; border:3px solid var(--coral);
}

@media (max-width:640px){
  .hdr{grid-template-columns:1fr auto; row-gap:12px}
  .hdr-mid{grid-column:1 / -1; grid-row:2; max-width:none}
  .tv{padding:10px 10px 6px; border-radius:26px}
  .screen{padding:14px 12px 12px}
  .tv-base .name{font-size:8px}
  .modes{flex-direction:column}
}
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important}
}
</style>
</head>
<body>
<main class="tv">
  <div class="screen" id="screen">
    <header class="hdr">
      <div class="hdr-left">
        <button class="btn" id="homeBtn" hidden>&#9666; HOME</button>
        <div class="logo"><b></b>AIJAGA</div>
      </div>
      <div class="hdr-mid">
        <span class="tiny" id="barText">LEVEL 1 &middot; HEALTH HERO</span>
        <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" id="bar"><i id="barFill"></i></div>
      </div>
      <div class="hdr-right">
        <button class="btn on" id="brightBtn">BRIGHT</button>
        <button class="btn" id="darkBtn">DARK</button>
      </div>
    </header>

    <section id="stage"></section>

    <p class="note">AiJaga shares general health information, not a diagnosis. In an emergency, call 999.</p>
    <canvas id="confetti" hidden></canvas>
  </div>
  <div class="tv-base">
    <div class="grille"><i></i><i></i><i></i><i></i><i></i></div>
    <div class="name">AIJAGA TV</div>
    <div class="knobs"><i></i><i></i><i class="dot"></i></div>
  </div>
</main>

<script>
const FIELDS = __QUIZ_DATA__;
const Q_PER = 3;

const $ = (s) => document.querySelector(s);
const stage = $("#stage");
const state = {
  field: null, quiz: null, qs: [], i: 0, score: 0, locked: false, timer: null, xp: 0,
  chat: [{ who: "bot", html: "Hi! I'm Dr. AiJaga. Ask me about a health topic, like <b>fever</b>, <b>asthma</b> or <b>cavities</b>." }]
};

/* ------------------------------ saved progress ------------------------------ */
const LS = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};
let progress = LS.get("aijaga-progress", {});
if (!progress || typeof progress !== "object") progress = {};
state.xp = Number(LS.get("aijaga-xp", 0)) || 0;

function qkey(fi, qi) { return FIELDS[fi].name + "|" + FIELDS[fi].quizzes[qi].title; }
function totalOf(fi, qi) { return Math.min(Q_PER, FIELDS[fi].quizzes[qi].questions.length); }
function getStatus(fi, qi) {
  const total = totalOf(fi, qi);
  const p = progress[qkey(fi, qi)];
  const a = p ? Math.max(0, Math.min(total, p.answered | 0)) : 0;
  const s = p ? Math.max(0, Math.min(a, p.score | 0)) : 0;
  if (a === 0) return { kind: "new", total: total };
  if (a >= total) return { kind: "done", answered: a, score: s, total: total };
  return { kind: "part", answered: a, score: s, total: total, pct: Math.round((a / total) * 100), left: total - a };
}

/* ------------------------------ pixel art ------------------------------ */
function pix(rows, pal, px) {
  const w = rows[0].length, h = rows.length;
  let rects = "";
  rows.forEach((row, y) => {
    [...row].forEach((c, x) => {
      if (pal[c]) rects += '<rect x="' + x + '" y="' + y + '" width="1.02" height="1.02" fill="' + pal[c] + '"/>';
    });
  });
  return '<svg class="pix" viewBox="0 0 ' + w + ' ' + h + '" width="' + (w * px) + '" height="' + (h * px) +
         '" shape-rendering="crispEdges" aria-hidden="true" style="display:block;image-rendering:pixelated">' + rects + "</svg>";
}
const DOC_PAL = { h: "#5b3a29", s: "#f2b88f", b: "#1b2a35", e: "#1b2a35", w: "#ffffff", g: "#2d6a5a", r: "#e07050", m: "#b8433f", k: "#cfd9d6" };
function doctor(mood, px) {
  const mouth = { happy: "bsmmmmsb", ok: "bssmmssb", flat: "bssssssb" }[mood] || "bssmmssb";
  const rows = [
    "......rr......", "....hhhhhh....", "...hhhhhhhh...", "...hssssssh...", "...sesssses...",
    "..." + mouth + "...", "...bbbbbbbb...", "....bbbbbb....", ".kwwwwggwwwwk.", "wwwwwwggwwwwww",
    "wwrwwwggwwwwww", "wwrwwwggwwwwww", "wwwrrwwggwwwww", "wwwwwwwwwwwwww", "wwwwwwwwwwwwww"
  ];
  return pix(rows, DOC_PAL, px || 8);
}
const PLAY = ["g.......", "gg......", "ggg.....", "gggg....", "ggggg...", "gggg....", "ggg.....", "gg......", "g......."];
const VIDEO_ICON = ["gggggggggg", "g........g", "g.g......g", "g.gg.....g", "g.ggg....g", "g.gg.....g", "g.g......g", "g........g", "gggggggggg"];

/* ------------------------------ helpers ------------------------------ */
function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function setBar(text, pct) {
  $("#barText").textContent = text;
  $("#barFill").style.width = pct + "%";
  $("#bar").setAttribute("aria-valuenow", Math.round(pct));
}
function levelBar() {
  const level = 1 + Math.floor(state.xp / 10);
  setBar("LEVEL " + level + " \u00B7 HEALTH HERO", (state.xp % 10) * 10);
}
function toast(msg) {
  const old = $(".toast"); if (old) old.remove();
  const t = document.createElement("div");
  t.className = "toast"; t.textContent = msg;
  $("#screen").appendChild(t);
  setTimeout(() => t.remove(), 2200);
}
function clearTimers() { if (state.timer) { clearTimeout(state.timer); state.timer = null; } stopConfetti(); }
function showHome(show) { $("#homeBtn").hidden = !show; }

/* ------------------------------ mini chat brain ------------------------------ */
/* Looks up the question in the quiz topics and answers from the quiz facts.   */
const STOP = new Set(["what","whats","why","how","does","are","the","and","for","with","can","you","about","tell","work","works","have","has","get","when","should","your","from","that","this","there","help","please","feel","cause","causes","caused","mean","means","body","some","not","too","very","any","who","was","were","will","into","their","them","then","than"]);
const ALIAS = {
  headache:"migraine", acne:"pimples", zit:"pimples", zits:"pimples", breathe:"respiratory", breathing:"respiratory",
  lung:"respiratory", lungs:"respiratory", poop:"constipation", poo:"constipation", pee:"urine", wee:"urine",
  sugar:"diabetes", tooth:"cavities", teeth:"cavities", mosquito:"dengue", mosquitoes:"dengue",
  seizure:"epilepsy", seizures:"epilepsy", memory:"alzheimer", stomach:"digestive", flu:"virus", cold:"virus",
  covid:"virus", dog:"rabies", hot:"heat", crowd:"stampede", sad:"depression", angry:"anger", faint:"faint",
  fainting:"faint", dizzy:"faint", rash:"chickenpox", cramps:"period", menstruation:"period", liver:"liver",
  kidney:"kidney", heartbeat:"heart", bp:"blood pressure"
};
const EMERGENCY = /(emergency|can'?t breathe|cannot breathe|not breathing|chest pain|unconscious|passed out|heavy bleeding|bleeding a lot|overdose|poison|suicid|kill myself|self[- ]harm)/i;

function stem(w) {
  w = w.replace(/[^a-z]/g, "");
  if (w.length > 5) w = w.replace(/ing$/, "");
  w = w.replace(/s$/, "").replace(/e$/, "");
  return w.slice(0, 5);
}
function tokens(s) {
  return s.toLowerCase().split(/[^a-z]+/).filter((w) => w.length >= 3 && !STOP.has(w)).map(stem).filter(Boolean);
}
const INDEX = [];
FIELDS.forEach((f, fi) => f.quizzes.forEach((q, qi) => INDEX.push({ fi: fi, qi: qi, title: q.title, stems: new Set(tokens(q.title)) })));

function findTopic(text) {
  const qs = new Set();
  text.toLowerCase().replace(/'/g, "").split(/[^a-z]+/).filter(Boolean).forEach((w) => {
    tokens(w).forEach((t) => qs.add(t));
    if (ALIAS[w]) tokens(ALIAS[w]).forEach((t) => qs.add(t));
  });
  let best = null, bestScore = 0;
  INDEX.forEach((it) => {
    let sc = 0; it.stems.forEach((s) => { if (qs.has(s)) sc++; });
    if (sc > bestScore) { best = it; bestScore = sc; }
  });
  return best;
}
function chipsHtml() {
  return '<div class="chips">' + shuffle(INDEX.slice()).slice(0, 5).map((x) =>
    '<button class="chip" data-act="ask" data-text="' + esc(x.title) + '">' + esc(x.title) + "</button>").join("") + "</div>";
}
function replyFor(text) {
  const t = text.toLowerCase();
  let html = "";
  const emergency = EMERGENCY.test(t);
  if (emergency) html += '<div class="alert">If this is an emergency, call 999 now or get a nearby adult to help.</div>';
  const hit = findTopic(t);
  if (hit) {
    const quiz = FIELDS[hit.fi].quizzes[hit.qi];
    html += "Here's what I know about <b>" + esc(quiz.title) + "</b>:<ul>" +
      quiz.questions.slice(0, Q_PER).map((q) => '<li><span class="fq">' + esc(q.q) + "</span>" + esc(q.answer) + "</li>").join("") +
      '</ul><div class="chips"><button class="chip go" data-act="quiz" data-f="' + hit.fi + '" data-q="' + hit.qi + '">TAKE THE QUIZ</button></div>' +
      '<span class="fine">General health information, not a diagnosis.</span>';
  } else if (emergency) {
    html += "I can only share general information here. Please get help from a trusted adult or emergency services.";
  } else if (/^\s*(hi|hello|hey|hai|salam|assalam)\b/.test(t)) {
    html += "Hello! What would you like to know? You can ask about:" + chipsHtml();
  } else {
    html += "I don't know that one yet. I can help with topics from the quiz library, like:" + chipsHtml();
  }
  return html;
}
function renderMsgs() {
  const box = $("#msgs"); if (!box) return;
  box.innerHTML = state.chat.map((m) => '<div class="msg ' + m.who + '">' + m.html + "</div>").join("");
  box.scrollTop = box.scrollHeight;
}
function sendChat(text) {
  text = (text || "").trim();
  if (!text) return;
  state.chat.push({ who: "me", html: esc(text) });
  state.chat.push({ who: "bot", html: "..." });
  renderMsgs();
  const idx = state.chat.length - 1;
  setTimeout(() => { state.chat[idx].html = replyFor(text); renderMsgs(); }, 450);
}
function openChat() { const z = $("#chatZone"); if (z) z.classList.add("open"); }
function maybeCloseChat() {
  const z = $("#chatZone"), inp = $("#chatIn");
  if (!z) return;
  const ae = document.activeElement;
  if (ae && z.contains(ae) && ae.id !== "chatStart") return;   // still typing or clicking inside
  if (inp && inp.value.trim()) return;                          // unsent draft
  z.classList.remove("open");
}
document.addEventListener("pointerdown", (e) => {
  const z = $("#chatZone");
  if (z && !z.contains(e.target)) maybeCloseChat();
});

/* ------------------------------ screens ------------------------------ */
function goHome() {
  clearTimers(); showHome(false); levelBar();
  stage.innerHTML =
    '<div class="home">' +
      '<div class="mascot"><div class="bob">' + doctor("happy", 8) + '</div><span class="tag">DR. AIJAGA</span></div>' +
      '<h1 class="hello">HI, I\'M DR. AIJAGA</h1>' +
      '<p class="hello-sub">Ask me about your health, or try a quiz.</p>' +
      '<div class="chat-zone" id="chatZone">' +
        '<button class="chat-start" id="chatStart" aria-label="Start chatting with Dr. AiJaga">' +
          '<span class="go">' + pix(PLAY, { g: "currentColor" }, 4) + 'START</span>' +
          '<span class="hint">Hover or tap here to ask Dr. AiJaga</span>' +
        '</button>' +
        '<div class="chat-panel" id="chatPanel">' +
          '<div class="msgs" id="msgs" role="log" aria-live="polite"></div>' +
          '<div class="chat-in"><input id="chatIn" type="text" maxlength="200" autocomplete="off" placeholder="Ask Dr. AiJaga a health question..." aria-label="Your question">' +
          '<button class="btn" id="sendBtn">SEND</button></div>' +
        '</div>' +
      '</div>' +
      '<div class="modes">' +
        '<button class="mode" data-mode="video">' + pix(VIDEO_ICON, { g: "currentColor" }, 3) + 'VIDEO</button>' +
        '<button class="mode" data-mode="quiz"><span class="qmark">(?)</span>QUIZ</button>' +
      '</div>' +
    '</div>';

  const z = $("#chatZone"), inp = $("#chatIn");
  renderMsgs();
  z.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") openChat(); });
  z.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") maybeCloseChat(); });
  $("#chatStart").addEventListener("click", () => { openChat(); requestAnimationFrame(() => inp.focus()); });
  const doSend = () => { const v = inp.value; inp.value = ""; sendChat(v); inp.focus(); };
  $("#sendBtn").addEventListener("click", doSend);
  inp.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); doSend(); }
    else if (e.key === "Escape") { inp.value = ""; inp.blur(); z.classList.remove("open"); }
  });
  inp.addEventListener("blur", () => setTimeout(() => { if (!z.matches(":hover")) maybeCloseChat(); }, 150));
  $("#msgs").addEventListener("click", (e) => {
    const b = e.target.closest("[data-act]"); if (!b) return;
    if (b.dataset.act === "ask") sendChat(b.dataset.text);
    else if (b.dataset.act === "quiz") startQuiz(+b.dataset.f, +b.dataset.q);
  });
  stage.querySelectorAll(".mode").forEach((b) => b.addEventListener("click", () => {
    if (b.dataset.mode === "quiz") goFields(); else toast("Videos are coming soon.");
  }));
}

function goFields() {
  clearTimers(); showHome(true); levelBar();
  let html = '<h1 class="title">( ? ) PICK A FIELD</h1><p class="sub">WHAT DO YOU WANT TO BE QUIZZED ON?</p><div class="grid">';
  FIELDS.forEach((f, fi) => {
    let done = 0, part = 0;
    f.quizzes.forEach((q, qi) => { const s = getStatus(fi, qi); if (s.kind === "done") done++; else if (s.kind === "part") part++; });
    const cls = done === f.quizzes.length ? "tile field done" : "tile field";
    html += '<button class="' + cls + '" data-f="' + fi + '"><h3>' + esc(f.name.toUpperCase()) + '</h3><span class="count">' +
      done + "/" + f.quizzes.length + " done" + (part ? " \u00B7 " + part + " in progress" : "") + "</span></button>";
  });
  html += "</div>";
  stage.innerHTML = html;
  stage.querySelectorAll(".tile").forEach((b) => b.addEventListener("click", () => goTitles(+b.dataset.f)));
}

function goTitles(fi) {
  clearTimers(); showHome(true); levelBar();
  state.field = fi;
  const f = FIELDS[fi];
  let html = '<h1 class="title">' + esc(f.name.toUpperCase()) + '</h1><p class="sub">PICK A TOPIC</p><div class="grid">';
  f.quizzes.forEach((q, qi) => {
    const s = getStatus(fi, qi);
    if (s.kind === "done") {
      html += '<button class="tile done" data-q="' + qi + '"><h3>' + esc(q.title.toUpperCase()) + '</h3><span class="count">\u2713 DONE \u00B7 ' + s.score + "/" + s.total + '</span></button>';
    } else if (s.kind === "part") {
      html += '<button class="tile part" data-q="' + qi + '"><h3>' + esc(q.title.toUpperCase()) + '</h3>' +
        '<div class="mini" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + s.pct + '"><i style="width:' + s.pct + '%"></i></div>' +
        '<span class="count">' + s.pct + "% done \u00B7 " + s.left + " left</span><span class=\"badge\">CONTINUE</span></button>";
    } else {
      html += '<button class="tile" data-q="' + qi + '"><h3>' + esc(q.title.toUpperCase()) + '</h3><span class="count">' + s.total + " questions</span></button>";
    }
  });
  html += '</div><div class="actions"><button class="btn small" id="backFields">&#9666; BACK TO FIELDS</button></div>';
  stage.innerHTML = html;
  stage.querySelectorAll(".tile").forEach((b) => b.addEventListener("click", () => startQuiz(fi, +b.dataset.q)));
  $("#backFields").addEventListener("click", goFields);
}

function startQuiz(fi, qi) {
  clearTimers(); showHome(true);
  state.field = fi; state.quiz = qi;
  const quiz = FIELDS[fi].quizzes[qi];
  state.qs = quiz.questions.slice(0, Q_PER).map((q) => ({
    q: q.q, answer: q.answer, opts: shuffle(Array.from(new Set(q.options)))
  }));
  const s = getStatus(fi, qi);
  const resume = s.kind === "part";                 // unfinished -> continue where they stopped
  state.i = resume ? s.answered : 0;
  state.score = resume ? s.score : 0;               // finished or new -> fresh attempt
  renderQuestion();
}

function updateQuizBar() {
  const total = state.qs.length;
  setBar("SCORE " + state.score + " / " + total + " \u00B7 QUESTION " + Math.min(state.i + 1, total) + " OF " + total, (state.i / total) * 100);
}

function renderQuestion() {
  const total = state.qs.length;
  const q = state.qs[state.i];
  state.locked = false;
  updateQuizBar();
  stage.innerHTML =
    '<h1 class="title">( ? ) ' + esc(FIELDS[state.field].quizzes[state.quiz].title.toUpperCase()) + '</h1>' +
    '<div class="qcard"><span class="qtag">QUESTION ' + (state.i + 1) + ' OF ' + total + '</span>' +
      '<div class="qbox"><p class="qtext">' + esc(q.q) + '</p>' +
      '<div class="opts" id="opts">' +
        q.opts.map((o, i) => '<button class="opt" data-i="' + i + '">' + esc(o) + '</button>').join("") +
      '</div><p class="feedback" id="fb"></p></div></div>';
  stage.querySelectorAll(".opt").forEach((b) => b.addEventListener("click", () => answer(b)));
}

function answer(btn) {
  if (state.locked) return;
  state.locked = true;
  const q = state.qs[state.i];
  const right = q.opts[+btn.dataset.i] === q.answer;
  const box = $("#opts");
  box.classList.add("locked");
  const fb = $("#fb");

  if (right) {
    btn.classList.add("ok");
    state.score++; state.xp++;
    fb.className = "feedback ok"; fb.textContent = "Correct!";
  } else {
    btn.classList.add("bad");
    box.querySelectorAll(".opt").forEach((b) => { if (q.opts[+b.dataset.i] === q.answer) b.classList.add("ok"); });
    fb.className = "feedback bad"; fb.textContent = "Not quite. The correct answer is in green.";
  }
  box.querySelectorAll(".opt").forEach((b) => { if (!b.classList.contains("ok") && !b.classList.contains("bad")) b.classList.add("dim"); });
  setBar("SCORE " + state.score + " / " + state.qs.length + " \u00B7 QUESTION " + (state.i + 1) + " OF " + state.qs.length, (state.i / state.qs.length) * 100);

  // save right away, so leaving mid-quiz keeps the progress
  progress[qkey(state.field, state.quiz)] = { answered: state.i + 1, score: state.score };
  LS.set("aijaga-progress", progress); LS.set("aijaga-xp", state.xp);

  state.timer = setTimeout(() => {
    state.i++;
    if (state.i < state.qs.length) renderQuestion(); else renderResult();
  }, right ? 1200 : 2200);
}

function renderResult() {
  const total = state.qs.length, s = state.score;
  setBar("SCORE " + s + " / " + total + " \u00B7 COMPLETE", 100);
  let msg, mood, celebrate = false, win = false;
  if (s === total) { msg = "Congrats, you nail it!"; mood = "happy"; celebrate = true; win = true; }
  else if (s === total - 1) { msg = "So close!"; mood = "ok"; celebrate = true; }
  else { msg = "It's okay, you can try again."; mood = "flat"; }

  stage.innerHTML =
    '<div class="result">' +
      '<div class="' + (celebrate ? "hop" : "") + '">' + doctor(mood, 10) + '</div>' +
      '<div class="score">YOU GOT ' + s + ' / ' + total + '</div>' +
      '<div class="msg2 ' + (win ? "win" : "") + '">' + esc(msg) + '</div>' +
      '<div class="actions">' +
        '<button class="btn big" id="again">TRY AGAIN</button>' +
        '<button class="btn big alt" id="other">TRY OTHER QUIZ</button>' +
      '</div>' +
    '</div>';
  $("#again").addEventListener("click", () => startQuiz(state.field, state.quiz));
  $("#other").addEventListener("click", goFields);
  if (celebrate) startConfetti();
}

/* ------------------------------ confetti ------------------------------ */
let confettiRaf = null;
function stopConfetti() {
  if (confettiRaf) cancelAnimationFrame(confettiRaf);
  confettiRaf = null;
  const cv = $("#confetti");
  cv.hidden = true;
  cv.getContext("2d").clearRect(0, 0, cv.width, cv.height);
}
function startConfetti() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = $("#confetti"), screen = $("#screen"), ctx = cv.getContext("2d");
  cv.hidden = false;
  cv.width = screen.clientWidth; cv.height = screen.clientHeight;
  const colors = ["#e07050", "#2d6a5a", "#f2c14e", "#4aa3df", "#ffffff", "#f08a68", "#7bd389"];
  const parts = [];
  const spawn = (n) => {
    for (let k = 0; k < n; k++) {
      parts.push({
        x: Math.random() * cv.width, y: -20 - Math.random() * 120,
        s: 6 + Math.floor(Math.random() * 7), vy: 1.8 + Math.random() * 2.6,
        vx: -1 + Math.random() * 2, c: colors[Math.floor(Math.random() * colors.length)],
        ph: Math.random() * Math.PI * 2
      });
    }
  };
  spawn(110);
  const start = performance.now();
  function frame(t) {
    ctx.clearRect(0, 0, cv.width, cv.height);
    if (t - start < 4500 && parts.length < 260) spawn(2);
    for (let i = parts.length - 1; i >= 0; i--) {
      const p = parts[i];
      p.y += p.vy; p.x += p.vx + Math.sin(p.y / 28 + p.ph) * 0.8;
      ctx.fillStyle = p.c;
      ctx.fillRect(Math.round(p.x), Math.round(p.y), p.s, p.s);
      if (p.y > cv.height + 20) parts.splice(i, 1);
    }
    if (parts.length || t - start < 4500) confettiRaf = requestAnimationFrame(frame);
    else stopConfetti();
  }
  confettiRaf = requestAnimationFrame(frame);
}

/* ------------------------------ theme + boot ------------------------------ */
function setTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  $("#brightBtn").classList.toggle("on", t === "bright");
  $("#darkBtn").classList.toggle("on", t === "dark");
  LS.set("aijaga-theme", t);
}
$("#brightBtn").addEventListener("click", () => setTheme("bright"));
$("#darkBtn").addEventListener("click", () => setTheme("dark"));
$("#homeBtn").addEventListener("click", goHome);

setTheme(LS.get("aijaga-theme", "bright") === "dark" ? "dark" : "bright");
goHome();
</script>
</body>
</html>
"""

PAGE = PAGE.replace("__QUIZ_DATA__", json.dumps([{"name": f["name"], "quizzes": f["quizzes"]} for f in FIELDS]))
