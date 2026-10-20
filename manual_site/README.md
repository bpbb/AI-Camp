# manual_site — เว็บคู่มือนักเรียน

เว็บ: https://ai-camp-chi.vercel.app

โฟลเดอร์นี้มีทุกอย่างของเว็บคู่มือในตัว ไม่ได้อ่านไฟล์จากโฟลเดอร์อื่นใน repo

| ที่ | คืออะไร |
|---|---|
| `docs/*.md` | เนื้อหาคู่มือ แก้ที่นี่ที่เดียว (ลำดับบทตามเลขหน้าชื่อไฟล์ ปิดท้ายด้วย `troubleshooting.md`) |
| `tools/` | ตัวแปลง `.md` เป็นหน้าเว็บ, CSS, JS และฟอนต์ IBM Plex Sans Thai (ฝังในหน้าเว็บ เปิดออฟไลน์ได้) |
| `build.sh` | build เป็น `public/index.html` เพื่อดูในเครื่อง |
| `vercel.json` | ตั้งค่าให้ Vercel build และ deploy |

## แก้คู่มือ

1. แก้ไฟล์ใน `docs/`
2. ดูผลในเครื่อง (ไม่บังคับ): `bash build.sh` แล้วเปิด `public/index.html`
3. commit แล้ว push ขึ้น `main` Vercel จะ build และอัปเดตเว็บเองภายในประมาณ 1 นาที

ไม่ต้อง commit `public/` เพราะ Vercel build ใหม่ทุกครั้ง

## ตั้งค่า Vercel (ทำครั้งเดียว)

ใน Vercel โปรเจกต์ `ai-camp` → Settings:

- **Git**: เชื่อมกับ repo `bpbb/AI-Camp`
- **Build and Deployment → Root Directory**: `manual_site`
- เปิด **Skip deployments when there are no changes to the root directory** เพื่อไม่ให้ deploy ใหม่เมื่อแก้โฟลเดอร์อื่น
