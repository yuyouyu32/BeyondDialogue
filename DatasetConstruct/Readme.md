# Dataset Construction

The `DatasetConstruct` codebase is responsible for **constructing role-playing dialogue datasets and alignment task datasets**, which is designed to construct role-playing (RP) dialogue datasets and perform alignment tasks across five key RP dimensions: **Character, Style, Emotion, Relationship, and Personality (CSERP)**. The resulting datasets are used for fine-tuning Large Language Models (LLMs) and creating derived training tasks.

- **Role Dialogue Dataset Construction:**
  - Generate role dialogue datasets from novel files and role profiles (`BeyondDialogue/data/Roles Info.xlsx`).
- **CSERP Alignment:**
  - Align dialogues and profiles in each scene of the role dialogue dataset across the five common role-playing dimensions: Character, Style, Emotion, Relationship, and Personality (CSERP).
  - This alignment process eliminates biases between the guiding prompts (profiles) and the resulting outputs (dialogues). The resulting CSERP dataset, which is finely aligned, has a volume five times larger than the original role-playing dialogue dataset.
- **LLMs Fine-tuning Dataset Construction:**
  - Construct fine-tuning datasets for Large Language Models (LLMs) using the role-playing and CSERP datasets.
  - Create two datasets: role-playing (without alignment) and RPA (with alignment).
  - Uniform the final training dataset size by sampling bilingual chit-chat datasets.


## Role-playing Dialogue and Alignment Dataset Construction

All bash commands should be executed from the code src directory of the repository. To navigate to the code src directory, use the following command `cd DatasetConstruct/src`.

### 1. Chunk Split and Filter
To manage the token limit of LLMs by splitting the novel into fixed-token chunks. Only chunks that meet the role's appearance threshold are retained to ensure relevant roles are captured while reducing the number of chunks and associated costs.

```bash
  python -m NovelSplit.split
```
### 2. Scenario Extract and Chunk Evaluation
Extract scenarios from chunks using open-source models, filtering out chunks containing multiple scenarios to maintain dialogue continuity. The selected model, Qwen1.5-72B-Chat, balances performance and efficiency. Additionally, chunks are evaluated to keep only those reflecting the role's profile.

```bash
python -m SceneExt.scene_ext
python -m ChunkEval.chunk_eval
```

### 3. Dialogue Extract
Extract dialogues and actions between roles from valid chunks using LLMs. The extracted dialogues are fundamental for RP training and derived tasks. GPT-4o is selected for its cost-effectiveness.

```bash
python -m DialogExt.extraction
```

### 4. Dialogue Check
Ensure valid RP dialogue data by forming alternating two-person dialogues, reconstructing scenarios, and maintaining coherence. GPT-4 is used to review role portrayal accuracy, discarding conflicting dialogues.

```bash
python -m SceneRecon.scene_regen
python -m ConflictCheck.conflict_check
```

### 5. Profile Alignment
- Align multi-turn dialogues across the CSERP dimensions using GPT-4o. The process involves recalling descriptive words for Character and Style, scoring Emotion and Relationship, and performing binary classification for Personality.

```bash
python -m DerivedTask.character
python -m DerivedTask.style
python -m DerivedTask.emotion
python -m DerivedTask.relationship
python -m DerivedTask.personality
```

### 6. Profile Adjustment
Adjust dialogue profiles based on alignment results. Predefined Character, Style, and Personality prompts are modified, while scene-dependent Emotion and Relationship information is added.

## Fine-tuning Dataset Formulation

To construct fine-tuning datasets for LLMs using the RP dialogue data, including aligned (RPA) and non-aligned (RP) versions, and the CSERP-derived training tasks.

### 1. Role-playing Dialogue Dataset
```bash
python -m SFTDataForm.RP_SFT_format
python -m SFTDataForm.RPA_SFT_format
```

### 2. CSERP Derived Training Tasks
```bash
python -m SFTDataForm.C_SFT_format
python -m SFTDataForm.S_SFT_format
python -m SFTDataForm.E_SFT_format
python -m SFTDataForm.R_SFT_format
python -m SFTDataForm.P_SFT_format
```

### 3. Chit-chat Dataset
```bash
python -m SFTDataForm.CC_SFT_format
```

>This code block contains a documentation comment that provides information about the file path and a note about filling in the API key for each model used in the code. It also mentions that if open-source models are being used, they need to be deployed manually.