# QFDB S1 — Google Forms build (bilingual ไทย/English, copy-paste ready)
*One form, age-screened (20+), birthday-routed, snowball-safe. ใช้คู่กับ `qfdb_s1_tally.py` → `chsh_analysis.py` + `qfdb_s1_nosignaling.py`.*

> **กฎเดียวที่ห้ามลืม:** แต่ละ option ของ §§4–7 **ต้องคงข้อความอังกฤษไว้** (รูป `English / ไทย`) เพราะ `tally.py` อ่าน coding จากส่วนอังกฤษ. ไทยปรับถ้อยคำได้ตามสบาย ขอแค่มีอังกฤษครบวลี

## A. Form settings
- Responses: Collect email = **OFF**; Limit to 1 response = **OFF** (anonymous).
- Presentation: Shuffle question order = **OFF**.
- คำถามตัวเลือกใน §§4–7: ⋮ → **Shuffle option order = ON**, **Required**.
- ชื่อ section §§4–7 เว้นว่าง/เป็นกลาง — ห้ามเผย condition หรือจุดประสงค์

## B. Title & description
- **Title:** Database Schemas as Quantum Fields — Category-Matching Survey / แบบสำรวจการจับคู่หมวดหมู่
  *(ชื่อที่แสดงต่อผู้ตอบใช้แบบกลางๆ ได้ ไม่ต้องโชว์ทฤษฎี)*
- **Description:**
  *A short, anonymous study on how people match category labels across systems (~2 min). Voluntary; stop anytime. No identifying information is collected and answers cannot be traced to you. Open to participants aged 20 and over. No foreseeable risk beyond everyday life. Questions: Arun Reungsilpkolkarn, arun.r@bu.ac.th.*
  *แบบสำรวจสั้น ไม่ระบุตัวตน เกี่ยวกับวิธีที่คนจับคู่ป้ายหมวดหมู่ข้ามระบบ (~2 นาที) เข้าร่วมโดยสมัครใจ หยุดเมื่อใดก็ได้ ไม่เก็บข้อมูลระบุตัวตน คำตอบสืบย้อนถึงตัวคุณไม่ได้ รับเฉพาะผู้มีอายุ 20 ปีขึ้นไป ไม่มีความเสี่ยงเกินชีวิตประจำวัน สอบถาม: Arun Reungsilpkolkarn, arun.r@bu.ac.th*

## C. Sections (9)

### Section 1 — การยินยอม / Informed Consent
**ใส่ในช่อง Description ของ section (ข้อความยืนยัน):**
> แบบสำรวจนี้เป็นส่วนหนึ่งของงานวิจัยเรื่องการจับคู่ป้ายหมวดหมู่ข้ามระบบ (~2 นาที, ไม่ระบุตัวตน, รับเฉพาะอายุ 20 ปีขึ้นไป) / This survey is part of a study on cross-system category matching (~2 min, anonymous, ages 20+).
>
> โดยการเลือก “ยินยอมเข้าร่วม” ด้านล่าง ข้าพเจ้ายืนยันว่า / By selecting “I consent” below, I confirm that:
> 1. ข้าพเจ้าได้อ่านและเข้าใจข้อมูลโครงการแล้ว / I have read and understood the study information.
> 2. ข้าพเจ้ามีอายุ 20 ปีขึ้นไป / I am 20 years of age or older.
> 3. การเข้าร่วมเป็นไปโดยสมัครใจ ถอนตัวได้ทุกเมื่อโดยไม่มีผลกระทบ / Participation is voluntary; I may withdraw at any time without consequence.
> 4. แบบสอบถามไม่ระบุตัวตน คำตอบสืบย้อนถึงตัวข้าพเจ้าไม่ได้ / The survey is anonymous; my responses cannot be traced to me.
> 5. ข้าพเจ้ายินยอมให้นำข้อมูลนิรนามไปวิเคราะห์และเผยแพร่ผลในภาพรวม / I consent to my anonymous data being used for analysis and aggregate reporting.
> สอบถาม / Contact: ดร.อรุณ เรืองศิลป์กลการ (Dr. Arun Reungsilpkolkarn), arun.r@bu.ac.th

**คำถาม (Multiple-choice, Required) → ตั้ง “Go to section based on answer”:**
**“ท่านยินยอมเข้าร่วมการวิจัยนี้หรือไม่? / Do you consent to take part in this research?”**
- `ยินยอมเข้าร่วม / I consent to take part` → **Section 2**
- `ไม่ประสงค์จะเข้าร่วม / I do not wish to take part` → **Section 9 (จบ)**

### Section 2 — Age eligibility / เกณฑ์อายุ  ⭐ ด่านคัดกรอง
Multiple-choice (Required) → ตั้ง **"Go to section based on answer"**:
**"What is your age range? / ช่วงอายุของคุณ?"**
- `Under 20 / ต่ำกว่า 20 ปี` → **Section 9 (ไม่เข้าเกณฑ์ — จบทันที)**
- `20–24` → **Section 3**
- `25–34` → **Section 3**
- `35–44` → **Section 3**
- `45 or older / 45 ปีขึ้นไป` → **Section 3**

*(ข้อนี้เก็บ "ช่วงอายุ" เป็น demographic ไปในตัว — ไม่ต้องถามซ้ำท้ายฟอร์ม)*

### Section 3 — (ชื่อกลางๆ เช่น "One quick question / คำถามสั้นๆ")
Multiple-choice (Required) → **"Go to section based on answer"**:
**"Which months is your birthday in? / วันเกิดของคุณอยู่ในช่วงเดือนใด?"**
- `January–March / มกราคม–มีนาคม` → **Section 4**
- `April–June / เมษายน–มิถุนายน` → **Section 5**
- `July–September / กรกฎาคม–กันยายน` → **Section 6**
- `October–December / ตุลาคม–ธันวาคม` → **Section 7**

### Instruction (วางใน Description ของ §§4–7 เหมือนกันทุก section)
*Two online marketplaces use different category labels for products. Which ONE pairing most naturally describes the same kind of product? Pick one.*
*ตลาดออนไลน์สองแห่งใช้ป้ายหมวดหมู่สินค้าต่างกัน คู่ใด "หนึ่งคู่" ที่อธิบายสินค้าชนิดเดียวกันได้เป็นธรรมชาติที่สุด? เลือกหนึ่งข้อ*
คำถาม (Required, shuffle ON): **"Best matching pair: / คู่ที่เข้ากันที่สุด:"**

### Section 4 *(AB)*
- Electronics + Gadget / อุปกรณ์อิเล็กทรอนิกส์ เครื่องใช้ไฟฟ้า + แกดเจ็ต
- Electronics + Decor / อุปกรณ์อิเล็กทรอนิกส์ เครื่องใช้ไฟฟ้า + ของแต่งบ้าน
- Furniture + Gadget / เฟอร์นิเจอร์ + แกดเจ็ต
- Furniture + Decor / เฟอร์นิเจอร์ + ของแต่งบ้าน

**หลัง §4 → "Go to Section 8".**

### Section 5 *(AB′)*
- Electronics + Toy / อุปกรณ์อิเล็กทรอนิกส์ เครื่องใช้ไฟฟ้า + ของเล่น
- Electronics + Hardware / อุปกรณ์อิเล็กทรอนิกส์ เครื่องใช้ไฟฟ้า + วัสดุก่อสร้าง
- Furniture + Toy / เฟอร์นิเจอร์ + ของเล่น
- Furniture + Hardware / เฟอร์นิเจอร์ + วัสดุก่อสร้าง

**หลัง §5 → "Go to Section 8".**

### Section 6 *(A′B)*
- Gift + Gadget / ของขวัญ + แกดเจ็ต
- Gift + Decor / ของขวัญ + ของแต่งบ้าน
- Tool + Gadget / เครื่องมือ + แกดเจ็ต
- Tool + Decor / เครื่องมือ + ของแต่งบ้าน

**หลัง §6 → "Go to Section 8".**

### Section 7 *(A′B′)*
- Gift + Toy / ของขวัญ + ของเล่น
- Gift + Hardware / ของขวัญ + วัสดุก่อสร้าง
- Tool + Toy / เครื่องมือ + ของเล่น
- Tool + Hardware / เครื่องมือ + วัสดุก่อสร้าง

**หลัง §7 → "Go to Section 8".**

### Section 8 — Final / ปิดท้าย (ผู้เข้าเกณฑ์ทุกคนมาที่นี่)
1. (Optional) **"How did you receive this survey? / คุณได้รับแบบสอบถามนี้จากทางใด?"** — Friend/เพื่อน · Workplace/ที่ทำงาน · University/มหาวิทยาลัย · Other/อื่นๆ
2. (Optional) Online-shopping frequency / ความถี่ช้อปออนไลน์ — Rarely/นานๆ ครั้ง · Sometimes/บางครั้ง · Often/บ่อย
→ **Submit** *(ไม่ต้องถามอายุซ้ำ — เก็บไปแล้วใน §2)*

### Section 9 — Not eligible / End — ไม่เข้าเกณฑ์ (ปลายทางของ "ต่ำกว่า 20" และ "ไม่ยินยอม")
Description (ไม่มีคำถาม): *"Thank you for your interest. This study is open to participants aged 20 and older. / ขอบคุณสำหรับความสนใจ การศึกษานี้รับเฉพาะผู้มีอายุ 20 ปีขึ้นไป"* → **Submit**

> **Routing must-checks (Preview ก่อนแชร์):** §§4–7 → §8; "ต่ำกว่า 20" และ "ไม่ยินยอม" → §9; ไม่มีใครเห็น condition อื่นนอกจากของตัวเอง

## D. Birthday → condition (3 เดือน/กลุ่ม = สมดุล, อิสระจากกลุ่มสังคม → snowball ปลอดภัย)
| birthday / วันเกิด | → section | condition |
|---|---|---|
| Jan–Mar / ม.ค.–มี.ค. | §4 | AB |
| Apr–Jun / เม.ย.–มิ.ย. | §5 | AB′ |
| Jul–Sep / ก.ค.–ก.ย. | §6 | A′B |
| Oct–Dec / ต.ค.–ธ.ค. | §7 | A′B′ |

## E. Coding key — สำหรับคุณ ไม่ใส่ในฟอร์ม (tally อ่านจากส่วนอังกฤษ)
| condition | pp (+,+) | pm (+,−) | mp (−,+) | mm (−,−) |
|---|---|---|---|---|
| AB  | Electronics+Gadget | Electronics+Decor | Furniture+Gadget | Furniture+Decor |
| AB′ | Electronics+Toy | Electronics+Hardware | Furniture+Toy | Furniture+Hardware |
| A′B | Gift+Gadget | Gift+Decor | Tool+Gadget | Tool+Decor |
| A′B′| Gift+Toy | Gift+Hardware | Tool+Toy | Tool+Hardware |
*(Electronics/Gift=+1, Furniture/Tool=−1 ; Gadget/Toy=+1, Decor/Hardware=−1)*

## F. After collection (ไม่ต้องนับมือ; คนต่ำกว่า 20 ถูกข้ามอัตโนมัติ เพราะไม่มี condition answer)
1. Forms → Responses → ⋮ → **Download responses (.csv)** → `forms_export.csv`
2. `python3 qfdb_s1_tally.py forms_export.csv` → `responses.csv`
3. `python3 chsh_analysis.py responses.csv` → S, 95% CI, verdict
4. `python3 qfdb_s1_nosignaling.py responses.csv` → marginal-law check
Decision rule (pre-register): violation iff CI-lower > 2 **และ** no-signaling holds

## G. หมายเหตุ
ป้ายหมวดหมู่ต้องอ่านเป็นธรรมชาติทั้งสองภาษา. ปรับคำไทยได้ **ตราบใดที่ส่วนอังกฤษยังครบ** tally/coding ไม่กระทบ. การคัดอายุที่ §2 ทำให้ไม่มีผู้เยาว์ (อายุต่ำกว่า 20 ตามกฎหมายไทย) เข้าร่วม — ตัดประเด็น parental consent ทิ้ง
