# Fleet & Field: Team Brief

Dell × NVIDIA GB10 hackathon, Boston, Saturday, October 3, 2026.

**Robots in the field need people in the field.** Fleet & Field is a 24/7 ops desk for a company that runs robot packing cells inside customers' warehouses around Boston. Two local agents share one Dell Pro Max GB10 and one Discord server. **Fleet** watches the robots, **Field** moves the people, and a service ticket connects them.

## The setting

The company installs and runs robot packing cells inside customers' buildings and charges for running them (robots-as-a-service). A small field team works out of one office and spends the day at outside appointments.

| Place | In the demo | What happens there |
|---|---|---|
| Our office | Seaport | 9:00 standup; where the day starts |
| Customer sites with our cells | Acme (Back Bay), Globex (Kendall) | The cells run orders. Engineers go there to set up new skills or fix problems |
| Prospects and clients | Initech, Northwind, the dinner downtown | Sales pitches, lunches, dinners |

- **Who travels:** sales engineers (pitch new customers) and field engineers (keep installed cells running). At a small company the same person often does both.
- **Why many customer sites and not two of our own factories:** with two fixed sites, travel is a single route at a known time and the Field agent would have almost nothing to plan. Many sites keep both halves of the project whole, and it's how real robot companies operate.

## Real-world analogs

- **Formic** is the closest to the business model. It runs robots-as-a-service: it installs robots in customers' factories, monitors them remotely with fleet dashboards, and sends field service technicians who travel between sites. Formic mostly uses conventionally programmed robots for palletizing, case packing and machine tending, not AI robot models.
- **Berkshire Grey** (Bedford, MA) is the closest to the robot cells. It builds AI-powered pick-and-pack, sorting and induction systems for e-commerce fulfillment centers, for Global 100 retailers and logistics companies.
- **Also in the Boston area:** Locus Robotics (warehouse mobile robots, sold as a subscription) and Vecna Robotics.
- **Pitch line:** "Think Formic's robots-as-a-service model with Berkshire Grey-style AI picking cells, run by two agents on one box."

## How it works

**Fleet (robot pair) watches the robots:**
- Takes work orders in each customer's channel and turns them into a plan of robot skills
- Runs the GR00T N1.7 robot model in the LIBERO simulator
- Refuses any skill it can't prove is reliable, and posts the failure clips
- Re-tests skills on a schedule and keeps a live reliability table
- Opens a service ticket when a cell needs a person on site

**Field (travel pair) moves the people:**
- Posts the morning brief: events, travel legs, tight connections, free slots, weather
- Answers "how many pitches today?" and "what's my availability?" from the calendar
- Computes MBTA and driving times with OpenTripPlanner running on the box
- Runs departure and attendance checks, and re-plans around delays
- Books service visits into the day and writes changes back to the calendar

**The loop:**
1. **Refuse.** Fleet won't run a skill the cell was never set up for, and opens a ticket.
2. **Book.** Field fits an engineer's visit into their day using free slots and live transit, and books it.
3. **Update.** An MBTA delay changes the ETA, and Fleet tells the customer.
4. **Commission.** The engineer taps "arrived". Fleet tests candidate robot models until it is 95% sure one succeeds at least 80% of the time. The gate opens and the order ships.

**Design rule:** code enforces, models explain. Counts, free slots, travel times and both safety gates are computed in code. The LLM decides what to say, whom to tag, and what to re-plan.

## Questions we've already worked through

**What does GR00T N1.7 do?**
It's the robot. It takes camera images, the arm's position and an instruction ("put the soup and the sauce in the basket") and outputs arm movements several times a second. It's a VLA (vision-language-action model): a vision-language model (Cosmos-Reason2-2B) reads the scene and the instruction, and a second network trained on demonstrations outputs short chunks of motor commands. It isn't agentic; it's the tool Fleet uses. Its unpredictable successes and failures are why a supervisor and a reliability check are needed at all.

**Isn't Fleet just if-then logic?**
The safety rules are code on purpose; "don't run an unproven skill" should never depend on an LLM following its prompt. The agent's real work is where judgment is needed:
- **Messy orders into a plan:** "pack 1042, the soup and the red can, and grab the spare from the drawer" means splitting it into skills, flagging what no skill covers, deciding whether to ship part of the order, and asking when it's ambiguous.
- **Diagnosing failures:** send the failure clip to Cosmos-Reason2 ("the gripper reaches the cabinet but never grasps the handle"), then decide between retrying, re-testing and opening a ticket. Serving it costs about 12 GB of memory.
- **Planning around deadlines:** decide how urgent a ticket is from today's pickups, and accept or push back on Field's proposed times ("4:30 misses the 5:00 pickup; 3:00 works").

**VLA or WAM?**
GR00T N1.7 is a VLA. NVIDIA's next generation, GR00T 2, is built on a world action model (WAM) from its DreamZero research, which predicts future video together with actions. DreamZero is a 14B model that controlled robots at 7 Hz and roughly doubled VLAs' success on new tasks in NVIDIA's tests. We use N1.7 because it has LIBERO checkpoints, runs on the GB10, and fits next to the LLM. Roadmap line: "with a world action model, Fleet can check the predicted outcome before dispatching."

**Is there reinforcement learning?**
Not in the core project. GR00T was trained by imitating demonstrations, and we only run it. What we add is **bandit commissioning**: a Thompson-sampling bandit splits test runs between candidate robot models and stops once it's 95% confident one is good enough. A raw success rate isn't enough: 9 of 10 gives only 68% confidence that the true rate is at least 80%, while 13 in a row gives 96%. In simulation it picks the right model in about 24 trials, against 40 for a fixed sweep. On a resume, call it a multi-armed bandit, not RL. The real RL follow-up after the event is PPO fine-tuning of GR00T with the open-source RLinf framework.

## The demo (about four minutes)

1. **Morning brief** (Field): the day's plan plus two fleet lines: Acme's cell is ready, Globex's cell can't do drawer tasks yet.
2. **Questions** (Field): "How many sales pitches today?" and "What's my availability?"
3. **Refusal** (Fleet): Globex posts a job that needs the drawer skill. Fleet refuses with failure clips and opens ticket T-12.
4. **Booking** (both): "You're in Kendall for the 2:30 pitch. Commissioning fits 3:00–3:45 before Initech at 4:00." One tap books it, and the calendar updates on screen.
5. **Delay** (Field): the 1:25 departure check finds an MBTA delay and offers "leave now or take a taxi". The new ETA reaches Globex.
6. **Commissioning** (Fleet): "Arrived." Test runs shift to the better robot model, the gate opens after about 24 trials, and the job ships.
7. **Recap** (both): one message covering the day and the fleet.

## Who builds what

- **Travel, person 1:** NemoClaw setup, both Discord bots, the Field agent, the demo clock
- **Travel, person 2:** field service: calendar, OpenTripPlanner, MBTA, weather, service visits
- **Robot, person 1:** GR00T policy servers, the LIBERO simulator, validation runs
- **Robot, person 2:** cell service: the gate, tickets, bandit commissioning, the Fleet agent

Each pair keeps about 90% of its original plan and owns one agent end to end. If either half breaks on the day, the other can still carry a demo.

## At the box this morning (robot side)

The HACK USB drive holds everything the robot side needs, so nothing big has to come over venue Wi-Fi: the GR00T + LIBERO image, the vLLM image NemoClaw uses, the Qwen3.6 and Cosmos-Reason2-2B models, and both GR00T checkpoints.

1. Plug in the drive (bring a USB-C adapter) and run `bash /media/$USER/HACK/setup_on_box.sh`. In about 15–25 minutes it copies everything to the internal disk, loads both images, checks the GPU, and starts both GR00T servers (`libero_10` on port 5555, `libero_goal` on 5556).
2. Wait for "Server is ready and listening" in `docker exec cell tail -f /tmp/gr00t_libero_10.log`.
3. Run the two smoke tests the script prints and time them; that sets how long live commissioning takes. Then run the drawer task on both servers: it should mostly fail on 5555 and mostly succeed on 5556.
4. Do NemoClaw onboarding (managed vLLM). The image and the Qwen weights are already in place, and NemoClaw's recipe caps vLLM at 40% of memory.

Good to know:
- GR00T contacts the Hugging Face website when loading Cosmos, even when it's cached. The checkpoints on the drive were patched to load Cosmos from a local folder, and this was tested with the network off. Details and the original files are in `notes/OFFLINE_FIX.md` on the drive.
- Nothing that needs the GPU (CUDA and rendering inside the image) could be tested before the event, so check that first if something breaks.
- If NemoClaw isn't preinstalled, its installer still needs Wi-Fi.

## Files and links

- Pitch page: https://claude.ai/artifact/HSCeF3C3NM6zoxKYL1sEYf (private until Thiago shares it from the page's Share menu)
- Full merged plan: `gb10-hackathon-integration.md` (ticket format, memory budget, fallbacks), in `notes/` on the drive
- Robot-side setup: `gb10-hackathon-handoff.md`, also in `notes/` on the drive
- Travel plan: `Travel_Ops_Agent_Channel_Assistant.docx`, also in `notes/` on the drive
