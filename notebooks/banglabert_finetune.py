# BanglaMind -- BanglaBERT Fine-tuning (Google Colab)
# =====================================================
# Runtime -> Change runtime type -> T4 GPU
# Cell গুলো Shift+Enter দিয়ে একে একে run করুন

# CELL 1: GPU + Libraries
# !nvidia-smi
# !pip install -q transformers==4.44.2 datasets==2.21.0 scikit-learn accelerate -q
# print("done")

# CELL 2: Drive Mount  
# from google.colab import drive; drive.mount("/content/drive")
# import os; SAVE_DIR="/content/drive/MyDrive/BanglaMind/model"; os.makedirs(SAVE_DIR,exist_ok=True)

# CELL 3: Load Data
# import pandas as pd
# df=pd.read_csv("https://raw.githubusercontent.com/jahidstm/banglamind/main/data/intents_dataset.csv")
# print(df["intent"].value_counts())

# CELL 4: Label Encode
# from sklearn.preprocessing import LabelEncoder
# from sklearn.model_selection import train_test_split
# le=LabelEncoder(); df["label"]=le.fit_transform(df["intent"])
# id2label={i:l for i,l in enumerate(le.classes_)}; label2id={l:i for i,l in id2label.items()}
# train_df,test_df=train_test_split(df,test_size=0.2,random_state=42,stratify=df["label"])

# CELL 5: Tokenizer
# from transformers import AutoTokenizer
# MODEL_NAME="csebuetnlp/banglabert"; tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME)

# CELL 6: Tokenize Dataset
# from datasets import Dataset
# def tok(e): return tokenizer(e["text"],truncation=True,padding="max_length",max_length=128)
# tr=Dataset.from_dict({"text":train_df["text"].tolist(),"label":train_df["label"].tolist()}).map(tok,batched=True)
# te=Dataset.from_dict({"text":test_df["text"].tolist(), "label":test_df["label"].tolist()}).map(tok,batched=True)

# CELL 7: Load Model
# import torch; from transformers import AutoModelForSequenceClassification
# device="cuda" if torch.cuda.is_available() else "cpu"
# model=AutoModelForSequenceClassification.from_pretrained(MODEL_NAME,num_labels=len(id2label),id2label=id2label,label2id=label2id).to(device)

# CELL 8: Training Args
# from transformers import TrainingArguments,Trainer
# from sklearn.metrics import accuracy_score,f1_score; import numpy as np
# def metrics(p): return {"accuracy":accuracy_score(p[1],p[0].argmax(-1)),"f1":f1_score(p[1],p[0].argmax(-1),average="weighted")}
# args=TrainingArguments("/content/ckpt",num_train_epochs=10,per_device_train_batch_size=16,
#   learning_rate=2e-5,evaluation_strategy="epoch",save_strategy="epoch",
#   load_best_model_at_end=True,metric_for_best_model="accuracy",fp16=True,report_to="none")

# CELL 9: TRAIN!
# trainer=Trainer(model=model,args=args,train_dataset=tr,eval_dataset=te,compute_metrics=metrics)
# r=trainer.train(); print(f"Loss: {r.training_loss:.4f}")

# CELL 10: Evaluate
# from sklearn.metrics import classification_report
# ev=trainer.evaluate(); print(f"Accuracy: {ev['eval_accuracy']*100:.2f}%")
# p=trainer.predict(te); print(classification_report(te["label"],p.predictions.argmax(-1),target_names=list(id2label.values())))

# CELL 11: Test
# import torch.nn.functional as F
# def pred(t):
#   inp={k:v.to(device) for k,v in tokenizer(t,return_tensors="pt",truncation=True,max_length=128).items()}
#   with torch.no_grad(): out=model(**inp)
#   pr=F.softmax(out.logits,-1); v,i=pr.max(-1)
#   return f"{id2label[i.item()]} ({v.item()*100:.0f}%)"
# for t in ["দাম কত?","কোথায়?","ডেলিভারি?","আস্সালামু আলাইকুম"]: print(f'"{t}" -> {pred(t)}')

# CELL 12: Save
# import json; trainer.save_model(SAVE_DIR); tokenizer.save_pretrained(SAVE_DIR)
# json.dump({"id2label":{str(k):v for k,v in id2label.items()},"label2id":label2id,
#   "accuracy":ev["eval_accuracy"],"model_name":MODEL_NAME},
#   open(f"{SAVE_DIR}/label_config.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
# print("Saved!")

# CELL 13 (OPTIONAL): HuggingFace Upload
# from huggingface_hub import notebook_login; notebook_login()
# HF="your-username/banglamind-banglabert"
# model.push_to_hub(HF); tokenizer.push_to_hub(HF)

# CELL 14: Download ZIP
# import shutil; from google.colab import files
# shutil.make_archive("/content/banglabert_model","zip",SAVE_DIR)
# files.download("/content/banglabert_model.zip")
