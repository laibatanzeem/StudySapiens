# chapter_content.py — hand-written chapter summaries for chapter pages.
#
# Keys: (class_id, subject_id, chapter_number) as used by build.py
# (class ids are strings "9"/"10"/"11"/"12"; subject ids are slugs like "physics").
#
# To enrich another chapter, add an entry here and re-run `python3 sync_files.py`.
# Fields (all optional except summary):
#   summary   : HTML paragraphs shown at the top of the chapter page
#   key_points: list of short bullet strings ("Key points to remember" box)
#   formulas  : list of (formula, what it means) tuples (small table)
#   tips      : HTML exam-tips text (shown in a callout)
#   faqs      : list of (question, answer-with-simple-HTML) tuples
#
# Only content that is standard textbook material and verified against the
# PCTB / PECTAA books should be added here — same rule as the rest of the site.

CHAPTER_CONTENT = {

    # ---------------- Class 9 Physics (new syllabus, 9 chapters) ----------------

    ("9", "physics", 1): {
        "summary": """
<p>Physics begins with measurement. A <b>physical quantity</b> is anything you can measure — length, mass, time, temperature — and every measurement needs two things: a number and a unit. This chapter sorts quantities into <b>base quantities</b> (the seven independent building blocks: length, mass, time, electric current, temperature, amount of substance, luminous intensity) and <b>derived quantities</b> (built by multiplying or dividing base quantities — speed is length ÷ time, force is mass × acceleration).</p>
<p>The world of science speaks one language of units: the <b>SI system</b>. You learn the base units (metre, kilogram, second, ampere, kelvin, mole, candela), the everyday <b>prefixes</b> from micro to mega, and how to write very large or small numbers neatly in <b>scientific notation</b> (e.g. 3.0 × 10<sup>8</sup> m/s — the speed of light).</p>
<p>The practical heart of the chapter is measuring instruments. A metre rule measures to 1 mm; <b>vernier callipers</b> measure length, diameter and depth to 0.1 mm; a <b>screw gauge</b> goes down to 0.01 mm. Each instrument has a <b>least count</b> (the smallest value it can read) and can suffer a <b>zero error</b>, which you must check and subtract. The chapter closes with <b>significant figures</b> — how many digits in a measurement honestly mean something.</p>""",
        "key_points": [
            "A physical quantity = numerical value × unit.",
            "Base quantities are independent (7 of them); derived quantities come from combining them.",
            "SI base units: metre (m), kilogram (kg), second (s), ampere (A), kelvin (K), mole (mol), candela (cd).",
            "Least count of vernier callipers = 0.1 mm; of a screw gauge = 0.01 mm.",
            "Always check zero error before measuring — then subtract it from your reading.",
            "In scientific notation, write numbers as a × 10ⁿ where 1 ≤ a < 10.",
            "Significant figures show the precision a measurement honestly supports.",
        ],
        "formulas": [
            ("Least count = smallest main-scale division ÷ number of vernier (or circular) divisions", "how fine an instrument can measure"),
            ("1 mm = 10⁻³ m, 1 µm = 10⁻⁶ m, 1 nm = 10⁻⁹ m", "prefix conversions examiners love"),
        ],
        "tips": "Board MCQs from this chapter are almost always about <b>least count, zero error and prefix conversion</b>. Practise reading vernier and screw-gauge diagrams until you can do them in ten seconds, and memorise the prefix ladder (micro, milli, kilo, mega). In numericals, convert everything to SI units <i>before</i> substituting — most marks are lost on unit slips.",
        "faqs": [
            ("Why do vernier callipers measure more precisely than a metre rule?",
             "Their vernier scale slides against the main scale, so they read 0.1 mm steps instead of the 1 mm steps of a rule. The finer the least count, the more precise the reading."),
            ("What is the difference between accuracy and precision?",
             "Accuracy is how close a reading is to the true value; precision is how finely and consistently an instrument can repeat a reading. A screw gauge is precise; a zero error makes it inaccurate until corrected."),
        ],
    },

    ("9", "physics", 2): {
        "summary": """
<p>Kinematics is the grammar of motion: describing <i>how</i> things move, without yet asking <i>why</i>. You start with rest and motion (both relative — a passenger is at rest with respect to the bus, moving with respect to the road), then meet the two families of quantities: <b>scalars</b> (magnitude only — distance, speed) and <b>vectors</b> (magnitude + direction — displacement, velocity, acceleration).</p>
<p>Distance is the full path travelled; <b>displacement</b> is the straight change of position, and it can be zero after a full round trip. Average speed = total distance ÷ total time, while velocity carries direction. <b>Acceleration</b> is the rate of change of velocity — a car speeding up, braking, or turning is accelerating.</p>
<p>Graphs turn motion into pictures: on a distance–time graph the slope is speed; on a speed–time graph the slope is acceleration and the <b>area under the graph is distance covered</b>. The chapter finishes with the three <b>equations of motion</b> and their most famous application, <b>free fall</b>, where gravity alone accelerates a body at g ≈ 9.8 m/s² downwards.</p>""",
        "key_points": [
            "Scalars: distance, speed, time. Vectors: displacement, velocity, acceleration, force.",
            "Displacement ≤ distance; they are equal only for straight-line motion with no turn back.",
            "Acceleration = change of velocity ÷ time; its unit is m/s².",
            "Slope of distance–time graph = speed; slope of speed–time graph = acceleration.",
            "Area under a speed–time graph = distance travelled.",
            "In free fall near Earth, a = g ≈ 9.8 m/s² (use 10 m/s² if the paper says so), and mass does not matter (ignoring air resistance).",
        ],
        "formulas": [
            ("v = s / t", "average speed (or velocity, with direction)"),
            ("a = (v<sub>f</sub> − v<sub>i</sub>) / t", "acceleration"),
            ("v<sub>f</sub> = v<sub>i</sub> + a t", "first equation of motion"),
            ("S = v<sub>i</sub> t + ½ a t²", "second equation of motion"),
            ("2 a S = v<sub>f</sub>² − v<sub>i</sub>²", "third equation of motion"),
        ],
        "tips": "Half the exam questions from this chapter are <b>equations-of-motion numericals</b> — always write down which three of the five quantities (v<sub>i</sub>, v<sub>f</sub>, a, t, S) you know, then pick the equation that contains your unknown. For graph questions, remember the two magic rules: <b>slope</b> tells you the rate, <b>area</b> tells you the total. In free-fall problems, take 'down' as one sign and stick to it.",
        "faqs": [
            ("Can a body have zero velocity but non-zero acceleration?",
             "Yes — at the highest point of a ball thrown upward, velocity is zero for an instant while gravity still accelerates it at 9.8 m/s²."),
            ("Is distance always greater than displacement?",
             "Distance is always greater than <i>or equal to</i> displacement. They are equal only for motion in a straight line without reversing."),
        ],
    },

    ("9", "physics", 3): {
        "summary": """
<p>Dynamics asks the question kinematics avoided: <b>why</b> do things move the way they do? The answer starts with <b>force</b> — a push or pull — and the property of matter called <b>inertia</b>: the laziness of a body to keep doing whatever it is doing. Mass is the measure of inertia.</p>
<p>The heart of the chapter is <b>Newton's three laws of motion</b>. The first (a body stays at rest or in uniform motion unless a net force acts) introduces inertia; the second gives the working formula <b>F = ma</b> (one newton is the force that gives 1 kg an acceleration of 1 m/s²); the third says forces come in equal-and-opposite pairs acting on <i>different</i> bodies. From the second law grows the idea of <b>momentum</b>, p = mv, and one of physics' most beautiful rules: in an isolated system, total momentum is <b>conserved</b> — the physics behind recoil of a gun, rocket propulsion, and collisions.</p>
<p>The chapter ends with <b>friction</b>, the force that opposes relative sliding. It is both a friend (walking, brakes, writing) and an enemy (wear, wasted energy), and engineers reduce it with lubrication, ball bearings and streamlined shapes.</p>""",
        "key_points": [
            "Inertia is the resistance of a body to a change in its state of motion; mass measures it.",
            "Newton's 1st law: no net force → no change in velocity.",
            "Newton's 2nd law: F = ma; unit of force is the newton (N = kg·m/s²).",
            "Newton's 3rd law: action and reaction are equal, opposite, and act on different bodies.",
            "Momentum p = mv (unit kg·m/s); in an isolated system total momentum stays constant.",
            "Friction opposes relative sliding; it depends on the surfaces and how hard they press.",
            "Rolling friction is much smaller than sliding friction — that is why wheels and ball bearings exist.",
        ],
        "formulas": [
            ("F = m a", "net force from mass and acceleration"),
            ("p = m v", "momentum of a body"),
            ("F = Δp / t", "force = rate of change of momentum (impulse form)"),
            ("m₁u₁ + m₂u₂ = m₁v₁ + m₂v₂", "conservation of momentum in a collision"),
        ],
        "tips": "Two question types dominate: <b>F = ma numericals</b> (watch the net force — subtract opposing forces before using the formula) and <b>momentum conservation</b> in collisions and recoil problems (draw before/after sketches and keep one direction positive). Never draw action and reaction on the same body — that is the classic MCQ trap.",
        "faqs": [
            ("If action and reaction are equal and opposite, why don't they cancel out?",
             "Because they act on <i>different</i> bodies. The earth pulls you down; you pull the earth up. Each body feels only one of the two forces, so neither is balanced by the other."),
            ("Why does a passenger fall forward when a bus brakes suddenly?",
             "Inertia: the lower body stops with the bus, but the upper body keeps moving forward because no force acts on it — Newton's first law in daily life."),
        ],
    },

    ("9", "physics", 4): {
        "summary": """
<p>A force can do more than push something along — it can <b>turn</b> things. This chapter studies the turning effect of forces. When a force acts on a body that has a pivot, its turning effect is called the <b>moment of force (torque)</b>: it grows with bigger force and longer perpendicular distance from the pivot. That is why door handles are far from the hinges and why a long spanner loosens a stubborn nut.</p>
<p>Forces themselves are vectors, so you learn to <b>add</b> them (head-to-tail rule) and to <b>resolve</b> them into perpendicular components (F<sub>x</sub> = F cos θ, F<sub>y</sub> = F sin θ). A pair of equal, opposite, parallel forces that produce pure rotation is called a <b>couple</b> — like the two hands on a steering wheel.</p>
<p>The chapter also locates the <b>centre of mass / centre of gravity</b> — the point where a body's weight can be considered to act — and closes with the two <b>conditions of equilibrium</b>: the sum of all forces must be zero (no change of motion) <i>and</i> the sum of all torques must be zero (no rotation). Master these and see-saws, beams and cranes become simple arithmetic.</p>""",
        "key_points": [
            "Torque (moment of force) = F × perpendicular distance from pivot; unit N m.",
            "Forces add as vectors (head-to-tail); they resolve into components F cos θ and F sin θ.",
            "A couple = two equal, opposite, parallel forces; its torque = F × distance between them.",
            "Centre of gravity is the point where the whole weight appears to act.",
            "First condition of equilibrium: ΣF = 0. Second condition: Στ = 0.",
            "A body in stable equilibrium returns after a small tilt; its centre of gravity rises when tilted.",
        ],
        "formulas": [
            ("τ = F × L", "torque (L = perpendicular distance from the pivot)"),
            ("F<sub>x</sub> = F cos θ, F<sub>y</sub> = F sin θ", "resolving a force into components"),
            ("Clockwise torque = Anticlockwise torque", "balance (principle of moments)"),
            ("Torque of a couple = F × d", "d = perpendicular distance between the two forces"),
        ],
        "tips": "Practise <b>see-saw and beam problems</b> until the principle of moments is reflex: choose the pivot, mark every force with its perpendicular distance, then set clockwise = anticlockwise. In resolution questions, always split along and perpendicular to the motion. MCQ setters like asking which equilibrium type a traffic cone / tightrope walker / ball in a bowl shows — learn one example of each.",
        "faqs": [
            ("Why is it easier to open a door by pushing at the handle than near the hinge?",
             "Torque = force × distance from the pivot. The same push at a larger distance gives a bigger turning effect, so the door turns more easily."),
            ("What is the difference between centre of mass and centre of gravity?",
             "For everyday sizes they are the same point. Centre of mass depends on how mass is spread; centre of gravity is where gravity's resultant torque is zero — they coincide in a uniform gravitational field."),
        ],
    },

    ("9", "physics", 5): {
        "summary": """
<p>In physics, <b>work</b> has a strict meaning: it is done only when a force actually moves something along its direction — W = F × S. Hold a heavy bag while standing still and, however tired you feel, you do zero physics work. The unit is the <b>joule</b>.</p>
<p>Working on a body stores or reveals <b>energy</b>. The two headline forms are kinetic energy (motion: ½mv²) and potential energy (position or shape: mgh for a raised body). Energy keeps transforming — a falling ball trades height for speed, a swinging pendulum trades it back — and the total stays constant: the <b>law of conservation of energy</b>. Power (P = W/t, measured in watts) is the <i>rate</i> of doing work, and <b>efficiency</b> compares useful output with total input — no real machine reaches 100%.</p>
<p>The new syllabus also connects this chapter to the real world: Pakistan's energy sources (hydro, coal, gas, solar, wind, nuclear), which are renewable and which are running out, and why the country faces load-shedding and an energy crisis.</p>""",
        "key_points": [
            "Work = force × distance in the direction of the force; W = F S cos θ; unit joule (J).",
            "Kinetic energy K.E. = ½ m v²; potential energy P.E. = m g h.",
            "Energy can neither be created nor destroyed, only transformed — the work–energy idea: work done = change in K.E.",
            "Power = work ÷ time; 1 watt = 1 joule/second; 1 kW = 1000 W.",
            "Efficiency = useful energy output ÷ total energy input × 100% — always below 100% for real machines.",
            "Renewable sources (sun, wind, hydro) replenish; non-renewable (coal, oil, gas) do not.",
        ],
        "formulas": [
            ("W = F S", "work by a force along its own direction"),
            ("K.E. = ½ m v²", "energy of motion"),
            ("P.E. = m g h", "energy stored by height"),
            ("P = W / t", "power"),
            ("Efficiency = (useful output / input) × 100%", "how good a machine really is"),
        ],
        "tips": "Numericals love chains: <b>drop a stone from h, find its speed at the ground</b> (set mgh = ½mv², watch the m cancel). Efficiency questions are easy marks — just keep output and input straight. For the theory part, prepare a short list of Pakistan's energy sources with one pro and one con each; the new syllabus asks about the energy crisis in context.",
        "faqs": [
            ("Why is no machine 100% efficient?",
             "Some input energy always escapes as heat, sound or friction. Efficiency only tells you the fraction of input that became useful output."),
            ("A pendulum swings forever in theory — why?",
             "Energy shuttles between potential (at the ends) and kinetic (at the middle) with no loss — conservation of energy. Real pendulums stop because friction and air resistance slowly steal the energy as heat."),
        ],
    },

    ("9", "physics", 6): {
        "summary": """
<p>Why do solids keep their shape, liquids pour, and gases spread everywhere? The <b>kinetic molecular model</b> answers: matter is made of particles whose spacing and freedom of movement set the state. In solids the particles only vibrate in fixed places; in liquids they slide past each other; in gases they fly free. Heat them enough and states change; at extreme temperature you even get <b>plasma</b>, the fourth state.</p>
<p>Two workhorse quantities follow. <b>Density</b> (ρ = m/V) tells how much mass is packed into a volume, and <b>pressure</b> (P = F/A) tells how concentrated a force is. Pressure explains why a sharp knife cuts and why elephants have wide feet. In liquids, pressure grows with depth (P = ρgh) and acts in all directions — <b>Pascal's law</b>, the idea behind hydraulic brakes and lifts.</p>
<p>Put a body in water and it feels an upward push — <b>upthrust</b>. Archimedes' principle says the upthrust equals the weight of fluid displaced; a body floats when the upthrust balances its weight. Finally, <b>Hooke's law</b> describes elastic materials: extension grows in proportion to the load, until the elastic limit.</p>""",
        "key_points": [
            "Solid: fixed shape; liquid: fixed volume, flowing shape; gas: neither; plasma: ionised gas.",
            "Density ρ = m / V (kg/m³); water is 1000 kg/m³.",
            "Pressure P = F / A (pascal); smaller area → larger pressure for the same force.",
            "Liquid pressure increases with depth: P = ρ g h, acting equally in all directions.",
            "Pascal's law: pressure applied to an enclosed liquid transmits undiminished everywhere (hydraulic machines).",
            "Archimedes: upthrust = weight of displaced fluid; floatation when upthrust = weight.",
            "Hooke's law: force ∝ extension (F = kx), valid up to the elastic limit.",
        ],
        "formulas": [
            ("ρ = m / V", "density"),
            ("P = F / A", "pressure"),
            ("P = ρ g h", "pressure at depth h in a liquid"),
            ("Upthrust = ρ<sub>fluid</sub> V g", "Archimedes' principle"),
            ("F = k x", "Hooke's law (k = spring constant, N/m)"),
        ],
        "tips": "Learn the <b>hydraulic press relation</b> (small piston in, big piston out — force multiplied by the area ratio) and the classic <b>float/block numericals</b>: a floating body displaces its own <i>weight</i> of fluid, a fully submerged one displaces its own <i>volume</i>. For Hooke's law, be ready to read a force–extension graph and mark the elastic limit.",
        "faqs": [
            ("Why does a steel ship float when steel itself sinks?",
             "The ship's hollow shape displaces a huge volume of water, so the upthrust equals the ship's whole weight. A solid block of steel displaces far less water than its weight, so it sinks."),
            ("Why do deep-sea divers need pressure suits?",
             "Liquid pressure grows with depth (P = ρgh). At great depths the water pressure would crush an unprotected diver's body."),
        ],
    },

    ("9", "physics", 7): {
        "summary": """
<p><b>Temperature</b> and <b>heat</b> are not the same thing: temperature is the degree of hotness (measured with a thermometer, in °C or K), while heat is <i>energy in transit</i> from a hotter body to a colder one (measured in joules). A thermometer works because liquids expand on heating — and you learn how fixed points (ice point, steam point) calibrate the scale.</p>
<p>Different materials warm up at different rates: water takes a lot of heat to raise its temperature — that property is <b>specific heat capacity</b> (c = ΔQ / mΔT, in J/(kg·K)). Water's unusually high value explains why it is used in car radiators and why coastal cities enjoy mild weather. Adding heat does not always raise temperature: at melting and boiling points the energy quietly goes into breaking bonds — <b>latent heat</b> (Q = mL) — which is why ice and water sit together at exactly 0 °C.</p>
<p>Finally, <b>thermal expansion</b>: nearly everything expands when heated. Linear expansion (ΔL = α L₀ ΔT) explains the gaps in railway tracks, sagging power lines, and bimetallic strips in thermostats.</p>""",
        "key_points": [
            "Temperature = degree of hotness (K, °C); heat = energy in transit (J); ΔK = Δ°C in size.",
            "Lower fixed point = melting ice (0 °C); upper = steam above boiling water (100 °C).",
            "Specific heat capacity c = ΔQ / (m ΔT); water's is 4200 J/(kg·K) — very high.",
            "During melting and boiling, temperature stays constant while latent heat is absorbed (Q = mL).",
            "Evaporation cools because the fastest molecules escape; it is faster with temperature, surface area and wind.",
            "Solids expand linearly on heating: ΔL = α L₀ ΔT.",
        ],
        "formulas": [
            ("Q = m c ΔT", "heat needed to change temperature (no state change)"),
            ("Q = m L", "latent heat for melting / boiling at constant temperature"),
            ("ΔL = α L₀ ΔT", "linear thermal expansion"),
            ("T(K) = T(°C) + 273", "Celsius ↔ kelvin"),
        ],
        "tips": "The exam favourite is the <b>mixing numerical</b>: hot metal dropped in water, heat lost = heat gained (m₁c₁ΔT₁ = m₂c₂ΔT₂). Draw the heating curve of water and mark the two flat plateaus — melting and boiling — because MCQs ask why temperature pauses there. For expansion, prepare two applications (railway gaps, bimetallic strip) and two precautions from daily life.",
        "faqs": [
            ("Why does steam burn worse than boiling water at the same temperature?",
             "Because steam first releases its latent heat of vaporisation (2.26 MJ/kg for water) while condensing — a huge hidden energy payment on top of the hot water."),
            ("Why is water used in car radiators?",
             "Its high specific heat capacity lets it absorb a lot of engine heat without its own temperature rising quickly."),
        ],
    },

    ("9", "physics", 8): {
        "summary": """
<p>Magnetism is one of the oldest sciences — and one of the most modern. A <b>magnet</b> has two poles (north-seeking and south-seeking); like poles repel and unlike poles attract, and breaking a magnet never isolates a single pole — every piece is again a full magnet with both ends.</p>
<p>Space around a magnet is changed: it carries a <b>magnetic field</b>, mapped by field lines drawn from N to S outside the magnet. The lines never cross, and where they crowd together the field is strongest. Sprinkle iron filings on paper over a bar magnet and you see this map appear. Materials split into families: <b>ferromagnetic</b> (iron, cobalt, nickel — strongly attracted and easy to magnetise), paramagnetic (weakly attracted) and diamagnetic (weakly repelled).</p>
<p>You also learn how magnets are made — stroking with another magnet, or with electric current (a coil wound around iron makes an <b>electromagnet</b>, switchable on and off) — and that the Earth itself is a giant magnet, which is why a compass needle settles along the field and points roughly north.</p>""",
        "key_points": [
            "Poles always come in pairs: a broken magnet is two smaller complete magnets.",
            "Like poles repel; unlike poles attract — the force acts without contact, through the field.",
            "Field lines run N → S outside the magnet; they never cross; closer lines = stronger field.",
            "Ferromagnetic materials (Fe, Co, Ni) are strongly attracted and can keep magnetism (hard) or lose it easily (soft iron).",
            "Methods of magnetisation: stroking, and electric current in a coil (electromagnet).",
            "The Earth behaves like a huge magnet; a compass aligns with its field.",
        ],
        "formulas": [],
        "tips": "Practise <b>sketching field-line patterns</b>: a single bar magnet, two like poles facing (repulsion — empty gap in the middle), and two unlike poles facing (attraction — lines pass straight through). MCQs love the 'broken magnet' idea — the answer is always 'each piece has both poles'. For electromagnets, remember the factors that strengthen them: more turns, more current, soft-iron core.",
        "faqs": [
            ("Can a magnet ever have a single pole?",
             "No. Cut a magnet anywhere and each piece instantly grows the missing pole. Physicists have searched for single poles (monopoles); none has been found."),
            ("Why does a compass not point exactly to geographic north?",
             "Because the Earth's magnetic poles do not coincide with its geographic poles. The angle between the two directions is called declination."),
        ],
    },

    ("9", "physics", 9): {
        "summary": """
<p>This closing chapter steps back and asks what science itself is. Science is not a pile of facts — it is a <i>method</i> for understanding nature: observe something carefully, form a testable guess (a <b>hypothesis</b>), experiment to test it, and let the results decide. A hypothesis that survives many independent tests can grow into a <b>theory</b> — a broad, tested explanation — while a <b>law</b> is a concise description of what nature always does (like Newton's laws).</p>
<p>Good science has habits: honest recording of data (even unwelcome results), repeating experiments, publishing methods so others can check them, and letting evidence overrule authority. Bad science — cherry-picked data, plagiarism, or claims that cannot be tested — is not science at all.</p>
<p>Finally the chapter connects physics to your world: the technology around you (mobile phones, MRI machines, power grids, satellites) grew directly from physics discoveries, and physics-trained people work in engineering, medicine, data, energy, teaching and research. Understanding how science works makes you a harder person to fool — and a better student of every subject.</p>""",
        "key_points": [
            "Scientific method: observation → hypothesis → experiment → analysis → conclusion, repeated.",
            "A hypothesis is a testable guess; a theory is a well-tested explanation; a law describes what always happens.",
            "Experiments need controlled variables: change one thing, measure one thing, keep the rest fixed.",
            "Honesty and repeatability are what separate science from opinion.",
            "Physics drives technology — and technology gives physics new tools (a two-way street).",
        ],
        "formulas": [],
        "tips": "This chapter's questions are usually <b>short conceptual ones</b>: name the steps of the scientific method, distinguish theory from law, or give an example of technology that came from physics. Prepare one clean example of a controlled experiment (one variable changed, one measured) and one Pakistan-relevant example of physics in technology — you can reuse both in many questions.",
        "faqs": [
            ("What is the difference between a theory and a law?",
             "A law summarises <i>what</i> happens (often as a formula); a theory explains <i>why</i> it happens. Both are strongly supported by evidence — neither is a weak guess."),
            ("Why is a hypothesis called 'testable'?",
             "Because it makes a prediction that an experiment could prove wrong. If no possible observation could contradict it, it is not science."),
        ],
    },
}
