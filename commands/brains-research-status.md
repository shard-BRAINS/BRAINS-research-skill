---
description: Read-only summary of the BRAINS research catalog — counts by category, recent additions, inbox and duplicate counts, integrity check
---

# /brains-research-status

Print a concise status report of the BRAINS research library. Read-only — never moves files or rewrites the catalog.

## Steps

1. Run `python -m scripts.status` from the skill root.

2. Format the JSON output as a human-readable summary:

   ```
   BRAINS Research Library — status

   Total catalogued:    <total>
   Inbox (pending):     <inbox_count>
   Duplicates folder:   <duplicates_count>

   By category:
     AI-General                    <n>
     AI-Ethics-Governance          <n>
     AI-Mental-Health              <n>
     AI-Neurodiversity-Autism      <n>
     AI-Education                  <n>
     Neurodiversity-General        <n>
     Autism                        <n>
     Suicide                       <n>
     Mental-Health-General         <n>
     HCI-Cognitive-Theory          <n>
     Extremism-Radicalisation      <n>

   Most recent additions (last 10):
     <YYYY> — <Author> — <title>          <category>
     ...

   Integrity:
     Catalog rows pointing at missing files: <n>
     Files on disk not in catalog:           <n>
   ```

3. If `missing_files` or `orphan_files` is non-empty, list each one and recommend the user inspect them. Do not auto-repair.

4. If the inbox count is non-zero, suggest running `/brains-research-process`.
