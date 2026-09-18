#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_data.py - Trích xuất và chuẩn hóa toàn bộ câu hỏi từ:
1. 【周边组长题库】2026年CESBG越南厂区线组长考试 Gốc.docx (Ngân hàng câu hỏi gốc - 201 câu)
2. 【周边组长题库】2026年CESBG越南厂区线组长考试 1.docx (Đề 1 - 60 câu chuẩn)
Lưu trữ vào:
- data/question_bank.json
- data/exam_de1.json
"""

import os
import re
import sys
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional
import docx
try:
    import fitz
except ImportError:
    fitz = None

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def clean_text(s: str) -> str:
    if not s:
        return ""
    # Chuẩn hóa khoảng trắng, dấu ngoặc và ký tự lạ
    s = s.replace('\u3000', ' ').replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def clean_q_title(text: str) -> str:
    """Loại bỏ tiền tố 'Câu X:' và dấu ngoặc trống '( )' ở cuối nếu có."""
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r'^Câu\s+\d+[:\.]\s*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[\(（]\s*[\)）]\s*$', '', t)
    return t.strip()


def extract_goc(docx_path: str):
    doc = docx.Document(docx_path)
    raw_paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    
    # Tiền xử lý: Tách dòng bị dính (P[846] dính "Câu 7: 10 điều cấm hàng đầu là?")
    paras = []
    for p in raw_paras:
        if "Câu 7: 10 điều cấm hàng đầu là?" in p and not p.startswith("Câu 7:"):
            parts = p.split("Câu 7: 10 điều cấm hàng đầu là?")
            paras.append(parts[0].strip())
            paras.append("Câu 7: 10 điều cấm hàng đầu là?")
        else:
            paras.append(p)
            
    # Xác định vị trí các phần (Section boundaries)
    sc_idx = -1
    mc_idx = -1
    tf_idx = -1
    sa_idx = -1
    cs_idx = -1
    
    for i, p in enumerate(paras):
        if "Chọn một đáp án đúng" in p and sc_idx == -1:
            sc_idx = i
        elif "Chọn nhiều đáp án đúng" in p and mc_idx == -1:
            mc_idx = i
        elif "Phán đoán đúng sai" in p and tf_idx == -1:
            tf_idx = i
        elif "Trả lời ngắn gọn" in p and sa_idx == -1:
            sa_idx = i
        elif "Phân tích tình huống" in p and cs_idx == -1:
            cs_idx = i
            
    # ----------------------------------------------------
    # 1. Phần I: Chọn một đáp án đúng (Single Choice)
    # ----------------------------------------------------
    sc_paras = paras[sc_idx + 1:mc_idx]
    single_choice_questions = []
    
    ans_regex = re.compile(r'[\(（]\s*([A-Da-d])\s*[\)）]\s*$')
    i = 0
    while i < len(sc_paras):
        p = sc_paras[i]
        m = ans_regex.search(p)
        
        # Nếu dòng hiện tại có chứa đáp án ở đuôi
        if m:
            ans = m.group(1).upper()
            q_text = p[:m.start()].strip()
            
            # Nếu câu hỏi bị tách thành 2 dòng (dòng trước là phần đầu câu hỏi)
            # Ví dụ: P[286] "Các vị trí cửa..." và P[287] "nào sau đây? (A)"
            if q_text.startswith(('nào sau đây', 'gì?', 'như thế nào')) or (q_text and q_text[0].islower()):
                if single_choice_questions and len(single_choice_questions[-1]['options']) > 0:
                    prev_part = single_choice_questions[-1]['options'].pop()
                    q_text = f"{prev_part} {q_text}"
            
            single_choice_questions.append({
                "id": f"SC_{len(single_choice_questions)+1:03d}",
                "type": "single_choice",
                "section": "Phần I: Chọn một đáp án đúng",
                "question": clean_q_title(q_text),
                "answer": ans,
                "options": []
            })
            i += 1
            continue
            
        # Nếu dòng hiện tại là câu hỏi nhưng đáp án nằm ở dòng tiếp theo (ví dụ: P[176] và P[177] là '（C）')
        if i + 1 < len(sc_paras) and ans_regex.match(sc_paras[i+1].strip()):
            next_m = ans_regex.match(sc_paras[i+1].strip())
            ans = next_m.group(1).upper()
            single_choice_questions.append({
                "id": f"SC_{len(single_choice_questions)+1:03d}",
                "type": "single_choice",
                "section": "Phần I: Chọn một đáp án đúng",
                "question": clean_q_title(p),
                "answer": ans,
                "options": []
            })
            i += 2
            continue
            
        # Là lựa chọn của câu hỏi hiện tại
        if single_choice_questions:
            # Kiểm tra dòng bị ngắt (dòng option nối tiếp)
            if p.startswith(('hiểm → Giới hạn', 'thành quy trình', 'nhóm lặp lại')):
                single_choice_questions[-1]['options'][-1] += " " + p
            else:
                single_choice_questions[-1]['options'].append(p)
        i += 1
        
    # ----------------------------------------------------
    # 2. Phần II: Chọn nhiều đáp án đúng (Multiple Choice)
    # ----------------------------------------------------
    mc_paras = paras[mc_idx + 1:tf_idx]
    multi_choice_questions = []
    mc_ans_regex = re.compile(r'[\(（]\s*([A-Ea-e,，、\s]+)\s*[\)）]\s*$')
    
    i = 0
    while i < len(mc_paras):
        p = mc_paras[i]
        # Word có thể đặt riêng đáp án ở đoạn kế tiếp: ghép trước khi parse,
        # tránh biến tiêu đề thành lựa chọn của câu trước và tạo câu rỗng.
        if i + 1 < len(mc_paras) and mc_ans_regex.fullmatch(mc_paras[i + 1]):
            p = f"{p} {mc_paras[i + 1]}"
            i += 1
        m = mc_ans_regex.search(p)
        if m:
            raw_ans = m.group(1)
            ans = "".join(re.findall(r'[A-Ea-e]', raw_ans)).upper()
            q_text = p[:m.start()].strip()
            
            multi_choice_questions.append({
                "id": f"MC_{len(multi_choice_questions)+1:03d}",
                "type": "multi_choice",
                "section": "Phần II: Chọn nhiều đáp án đúng",
                "question": clean_q_title(q_text),
                "answer": ans,
                "options": []
            })
            i += 1
            continue
            
        if multi_choice_questions:
            multi_choice_questions[-1]['options'].append(p)
        i += 1

    # ----------------------------------------------------
    # 3. Phần III: Phán đoán đúng/sai (True / False)
    # ----------------------------------------------------
    tf_paras = paras[tf_idx + 1:sa_idx]
    true_false_questions = []
    
    # Ghép các dòng bị ngắt trong phần Đúng/Sai
    merged_tf = []
    skip_next = False
    for idx, p in enumerate(tf_paras):
        if skip_next:
            skip_next = False
            continue
        # Dòng bị cắt: kết thúc bằng 'là' và dòng sau có (V)
        if p.endswith("là") and idx + 1 < len(tf_paras):
            merged_tf.append(f"{p} {tf_paras[idx+1]}")
            skip_next = True
        else:
            merged_tf.append(p)
            
    for p in merged_tf:
        # Tìm ký hiệu đáp án V/X/T/F/√/×
        m = re.search(r'[\(（]?\s*([VXvx√×])\s*[\)）]+', p)
        if m:
            val = m.group(1).upper()
            ans = "V" if val in ("V", "√") else "X"
            # Cắt bỏ ký hiệu đáp án để lấy nội dung câu khẳng định
            q_text = re.sub(r'[\(（]?\s*[VXvx√×]\s*[\)）]+', '', p).strip()
            # Dọn dẹp dấu câu ở cuối nếu có
            q_text = q_text.rstrip(' :;.,')
            true_false_questions.append({
                "id": f"TF_{len(true_false_questions)+1:03d}",
                "type": "true_false",
                "section": "Phần III: Phán đoán đúng sai",
                "question": clean_q_title(q_text),
                "answer": ans,
                "options": ["V. Đúng (Đúng theo quy định)", "X. Sai (Sai quy định / Không chính xác)"]
            })
            
    # ----------------------------------------------------
    # 4. Phần IV: Trả lời ngắn gọn (Short Answer)
    # ----------------------------------------------------
    sa_paras = paras[sa_idx + 1:cs_idx]
    short_answer_questions = []
    cur_sa = None
    
    for p in sa_paras:
        if re.match(r'^Câu\s+\d+[:\.]', p):
            if cur_sa:
                short_answer_questions.append(cur_sa)
            # Tách nội dung câu hỏi
            q_text = p
            # Nếu câu hỏi có dính "Câu trả lời tham khảo:" ở đuôi
            if "Câu trả lời tham khảo:" in q_text:
                q_text = q_text.split("Câu trả lời tham khảo:")[0].strip()
            elif "Đáp án tham khảo:" in q_text:
                q_text = q_text.split("Đáp án tham khảo:")[0].strip()
                
            cur_sa = {
                "id": f"SA_{len(short_answer_questions)+1:03d}",
                "type": "short_answer",
                "section": "Phần IV: Trả lời ngắn gọn",
                "question": clean_q_title(q_text),
                "answer": []
            }
        else:
            if cur_sa:
                if p not in ("Câu trả lời tham khảo:", "Đáp án tham khảo:"):
                    cur_sa["answer"].append(p)
    if cur_sa:
        short_answer_questions.append(cur_sa)

    # ----------------------------------------------------
    # 5. Phần V: Phân tích tình huống (Case Study)
    # ----------------------------------------------------
    cs_paras = paras[cs_idx + 1:]
    case_study_questions = []
    cur_cs = None
    
    for p in cs_paras:
        if re.match(r'^Câu\s+\d+[:\.]', p):
            if cur_cs:
                case_study_questions.append(cur_cs)
            cur_cs = {
                "id": f"CS_{len(case_study_questions)+1:03d}",
                "type": "case_study",
                "section": "Phần V: Phân tích tình huống",
                "question_parts": [p],
                "answer_parts": [],
                "in_answer": False
            }
        else:
            if cur_cs:
                if "Đáp án tham khảo" in p or "Câu trả lời tham khảo" in p:
                    cur_cs["in_answer"] = True
                elif cur_cs["in_answer"]:
                    cur_cs["answer_parts"].append(p)
                else:
                    cur_cs["question_parts"].append(p)
    if cur_cs:
        case_study_questions.append(cur_cs)
        
    for cs in case_study_questions:
        cleaned_parts = [clean_q_title(part) for part in cs.pop("question_parts") if part.strip()]
        cs["question"] = "\n".join(cleaned_parts)
        cs["answer"] = cs.pop("answer_parts")

    # Chuẩn hóa tiền tố A., B., C., D. cho options nếu chưa có
    for q in single_choice_questions + multi_choice_questions:
        norm_opts = []
        letters = ["A", "B", "C", "D", "E", "F"]
        for idx, opt in enumerate(q["options"]):
            if re.match(r'^[A-F][\.\:\s]', opt):
                norm_opts.append(opt)
            else:
                letter = letters[idx] if idx < len(letters) else f"({idx+1})"
                norm_opts.append(f"{letter}. {opt}")
        q["options"] = norm_opts

    all_questions = (
        single_choice_questions +
        multi_choice_questions +
        true_false_questions +
        short_answer_questions +
        case_study_questions
    )
    
    return {
        "title": "Ngân hàng câu hỏi xét thăng chức tổ trưởng CESBG Việt Nam 2026",
        "total_questions": len(all_questions),
        "counts": {
            "single_choice": len(single_choice_questions),
            "multi_choice": len(multi_choice_questions),
            "true_false": len(true_false_questions),
            "short_answer": len(short_answer_questions),
            "case_study": len(case_study_questions)
        },
        "questions": all_questions
    }


def extract_exam1(docx_path: str, bank_data: dict):
    doc = docx.Document(docx_path)
    paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    
    bank_questions = bank_data["questions"]
    
    def find_match(q_text: str, q_type: str):
        def normalized(text):
            return re.sub(r'\W+', '', clean_q_title(text), flags=re.UNICODE).casefold()

        target = normalized(q_text)
        if not target:
            return None
        candidates = [(q, normalized(q["question"])) for q in bank_questions
                      if q["type"] == q_type and normalized(q["question"])]
        exact = [q for q, title in candidates if title == target]
        if len(exact) == 1:
            return exact[0]
        # Tự luận/tình huống có thể gồm nhiều đoạn; chỉ chấp nhận tiền tố
        # đầy đủ, duy nhất. Không ghép theo 28 ký tự hoặc chuỗi rỗng.
        if not exact and q_type in ("short_answer", "case_study"):
            matches = [q for q, title in candidates if title.startswith(target)]
            if len(matches) == 1:
                return matches[0]
        return None

    cur_sec = ""
    exam_questions = []
    cur_q = None
    
    for p in paras:
        if "I. Chọn một đáp án đúng" in p:
            cur_sec = "single_choice"
            continue
        elif "II. Chọn nhiều đáp án đúng" in p:
            cur_sec = "multi_choice"
            continue
        elif "III. Phán đoán đúng sai" in p:
            cur_sec = "true_false"
            continue
        elif "IV. Trả lời ngắn gọn" in p:
            cur_sec = "short_answer"
            continue
        elif "V. Phân tích tình huống" in p:
            cur_sec = "case_study"
            continue

        if re.match(r'^Câu\s+\d+[:\.]', p):
            if cur_q:
                exam_questions.append(cur_q)
            
            matched = find_match(p, cur_sec)
            cur_q = {
                "num": len(exam_questions) + 1,
                "type": cur_sec,
                "question": clean_q_title(p),
                "answer": deepcopy(matched["answer"]) if matched else "",
                "options": list(matched.get("options", [])) if matched else [],
                "matched_id": matched["id"] if matched else None
            }
        else:
            if cur_q:
                if re.match(r'^[A-D]\.', p):
                    if not cur_q.get("options") or len(cur_q["options"]) < 2:
                        cur_q.setdefault("options", []).append(p)
                elif cur_sec in ("case_study", "short_answer"):
                    cur_q["question"] += "\n" + clean_q_title(p)

    if cur_q:
        exam_questions.append(cur_q)
        
    return {
        "title": "Đề thi xét thăng chức tổ trưởng CESBG Việt Nam (Đề 1)",
        "total_questions": len(exam_questions),
        "questions": exam_questions
    }


def validate_data(bank_data, exam_data):
    """Chặn dữ liệu rỗng/không ghép được trước khi thay thế JSON đang dùng."""
    for q in bank_data["questions"] + exam_data["questions"]:
        label = q.get("id", q.get("num"))
        if not q.get("question", "").strip() or not q.get("answer"):
            raise ValueError(f"Câu {label}: thiếu nội dung hoặc đáp án")
        if q["type"] in ("single_choice", "multi_choice"):
            options = q.get("options", [])
            labels = [opt[:1] for opt in options]
            if not 2 <= len(options) <= 6 or labels != list("ABCDEF"[:len(options)]):
                raise ValueError(f"Câu {label}: lựa chọn không hợp lệ")
            if not set(q["answer"]) <= set(labels):
                raise ValueError(f"Câu {label}: đáp án không thuộc lựa chọn")
    if any(not q.get("matched_id") for q in exam_data["questions"]):
        raise ValueError("Đề 1 có câu chưa ánh xạ duy nhất với ngân hàng gốc")


def extract_chuyen_truong_pdf(pdf_path: str) -> Dict[str, Any]:
    """Trích xuất và chuẩn hóa 255 câu hỏi từ file PDF Đề Chuyền Trưởng."""
    if fitz is None:
        raise ImportError("Cần cài đặt PyMuPDF (fitz) để đọc file PDF: pip install pymupdf")
        
    doc = fitz.open(pdf_path)
    header_patterns = [
        r'CESBG\s*越南厂区拟晋升线组长资格考试复习题.*',
        r'Đề\s*ôn tập kỳ\s*thi xét thăng chức chuyền tổ\s*trưởng CESBG Việt Nam.*',
        r'版次:\s*\w+',
        r'Phiên bản:\s*\w+',
        r'Trang\s+\d+/\d+',
        r'\(Mang tính chất tham khảo\)',
        r'Đề ôn tập kỳ thi xét thăng chức chuyền tổ trưởng CESBG Việt Nam – Đề chuyền trưởng'
    ]

    raw_lines = []
    for page in doc:
        for line in page.get_text('text').split('\n'):
            l = line.strip()
            if l and not any(re.match(hp, l, re.IGNORECASE) for hp in header_patterns):
                raw_lines.append(l)

    sec_starts = {}
    for i, l in enumerate(raw_lines):
        if re.match(r'^I\.\s*Chọn một đáp án đúng', l):
            sec_starts['I'] = i
        elif re.match(r'^II\.\s*Chọn nhiều đáp án đúng', l):
            sec_starts['II'] = i
        elif re.match(r'^III\.\s*Phán đoán đúng sai', l):
            sec_starts['III'] = i
        elif re.match(r'^IV\.\s*Trả lời ngắn gọn', l):
            sec_starts['IV'] = i
        elif re.match(r'^V\.\s*Phân tích tình huống', l):
            sec_starts['V'] = i

    # 1. Phần I: Chọn một đáp án đúng
    lines_I = raw_lines[sec_starts['I']+1 : sec_starts['II']]
    ans_regex_sc = re.compile(r'[\(（]\s*([A-Da-d])\s*[\)）]')
    q_blocks_I = []
    cur_q = None
    for l in lines_I:
        m = re.match(r'^(\d+)[\.、]\s*(.*)', l)
        if m:
            if cur_q:
                q_blocks_I.append(cur_q)
            cur_q = {'num': int(m.group(1)), 'lines': [m.group(2).strip()]}
        elif cur_q:
            cur_q['lines'].append(l)
    if cur_q:
        q_blocks_I.append(cur_q)

    sc_questions = []
    for qb in q_blocks_I:
        lines = qb['lines']
        first_opt = -1
        for i, l in enumerate(lines):
            if re.search(r'(^|\s+)A\.\s*', l):
                first_opt = i
                break
        q_lines = lines[:first_opt]
        opt_lines = lines[first_opt:]
        m_split = re.search(r'(.*?)(A\.\s*.*)', opt_lines[0])
        if m_split and m_split.group(1).strip():
            q_lines.append(m_split.group(1).strip())
            opt_lines[0] = m_split.group(2).strip()
        q_text = ' '.join(q_lines).strip()
        ans_m = list(ans_regex_sc.finditer(q_text))
        answer = ans_m[-1].group(1).upper() if ans_m else ""
        q_text = ans_regex_sc.sub('', q_text).strip()
        q_text = re.sub(r'[\(（]\s*[\)）]', '', q_text).strip()
        opt_full = ' '.join(opt_lines)
        opts = [o.strip() for o in re.split(r'(?=[A-D]\.\s*)', opt_full) if o.strip()]
        sc_questions.append({
            'id': f"SC_{len(sc_questions)+1:03d}",
            'type': 'single_choice',
            'section': 'Phần I: Chọn một đáp án đúng',
            'question': clean_q_title(q_text),
            'answer': answer,
            'options': opts
        })

    # 2. Phần II: Chọn nhiều đáp án đúng
    lines_II = raw_lines[sec_starts['II']+1 : sec_starts['III']]
    ans_regex_mc = re.compile(r'[\(（]\s*([A-Fa-f,，、\s]+)\s*[\)）]')
    q_blocks_II = []
    cur_q = None
    for l in lines_II:
        m = re.match(r'^(\d+)[\.、]\s*(.*)', l)
        if m:
            if cur_q:
                q_blocks_II.append(cur_q)
            cur_q = {'num': int(m.group(1)), 'lines': [m.group(2).strip()]}
        elif cur_q:
            cur_q['lines'].append(l)
    if cur_q:
        q_blocks_II.append(cur_q)

    mc_questions = []
    for qb in q_blocks_II:
        lines = qb['lines']
        first_opt = -1
        for i, l in enumerate(lines):
            if re.search(r'(^|\s+)A\.\s*', l):
                first_opt = i
                break
        q_lines = lines[:first_opt]
        opt_lines = lines[first_opt:]
        m_split = re.search(r'(.*?)(A\.\s*.*)', opt_lines[0])
        if m_split and m_split.group(1).strip():
            q_lines.append(m_split.group(1).strip())
            opt_lines[0] = m_split.group(2).strip()
        q_text = ' '.join(q_lines).strip()
        ans_m = list(ans_regex_mc.finditer(q_text))
        answer = "".join(re.findall(r'[A-Fa-f]', ans_m[-1].group(1))).upper() if ans_m else ""
        q_text = ans_regex_mc.sub('', q_text).strip()
        q_text = re.sub(r'[\(（]\s*[\)）]', '', q_text).strip()
        opt_full = ' '.join(opt_lines)
        opts = [o.strip() for o in re.split(r'(?=[A-F]\.\s*)', opt_full) if o.strip()]
        mc_questions.append({
            'id': f"MC_{len(mc_questions)+1:03d}",
            'type': 'multi_choice',
            'section': 'Phần II: Chọn nhiều đáp án đúng',
            'question': clean_q_title(q_text),
            'answer': answer,
            'options': opts
        })

    # 3. Phần III: Phán đoán đúng sai
    lines_III = raw_lines[sec_starts['III']+1 : sec_starts['IV']]
    ans_regex_tf = re.compile(r'[\(（]?\s*([VXvx√×])\s*[\)）]+')
    q_blocks_III = []
    cur_q = None
    for l in lines_III:
        m = re.match(r'^(\d+)[\.、]\s*(.*)', l)
        if m:
            if cur_q:
                q_blocks_III.append(cur_q)
            cur_q = {'num': int(m.group(1)), 'lines': [m.group(2).strip()]}
        elif cur_q:
            cur_q['lines'].append(l)
    if cur_q:
        q_blocks_III.append(cur_q)

    tf_questions = []
    for qb in q_blocks_III:
        full_text = ' '.join(qb['lines']).strip()
        ans_m = list(ans_regex_tf.finditer(full_text))
        val = ans_m[-1].group(1).upper()
        ans = 'V' if val in ('V', '√') else 'X'
        q_text = full_text[:ans_m[-1].start()] + full_text[ans_m[-1].end():]
        q_text = re.sub(r'[\(（]\s*[\)）]', '', q_text).strip().rstrip(' :;.,')
        tf_questions.append({
            'id': f"TF_{len(tf_questions)+1:03d}",
            'type': 'true_false',
            'section': 'Phần III: Phán đoán đúng sai',
            'question': clean_q_title(q_text),
            'answer': ans,
            'options': ["V. Đúng (Đúng theo quy định)", "X. Sai (Sai quy định / Không chính xác)"]
        })

    # 4. Phần IV: Trả lời ngắn gọn
    lines_IV = raw_lines[sec_starts['IV']+1 : sec_starts['V']]
    sa_blocks = []
    cur_sa = None
    for l in lines_IV:
        m = re.match(r'^(\d+)[\.、]\s*(.*)', l)
        if m and (cur_sa is None or cur_sa.get('has_ans', False)):
            if cur_sa:
                sa_blocks.append(cur_sa)
            cur_sa = {'num': int(m.group(1)), 'q_lines': [m.group(2).strip()], 'ans_lines': [], 'has_ans': False}
        elif cur_sa:
            if 'Đáp án tham khảo:' in l or 'Câu trả lời tham khảo:' in l:
                cur_sa['has_ans'] = True
                rest = l.replace('Đáp án tham khảo:', '').replace('Câu trả lời tham khảo:', '').strip()
                if rest:
                    cur_sa['ans_lines'].append(rest)
            elif cur_sa['has_ans']:
                cur_sa['ans_lines'].append(l)
            else:
                cur_sa['q_lines'].append(l)
    if cur_sa:
        sa_blocks.append(cur_sa)

    sa_questions = []
    for qb in sa_blocks:
        q_text = ' '.join(qb['q_lines']).strip()
        sa_questions.append({
            'id': f"SA_{len(sa_questions)+1:03d}",
            'type': 'short_answer',
            'section': 'Phần IV: Trả lời ngắn gọn',
            'question': clean_q_title(q_text),
            'answer': qb['ans_lines']
        })

    # 5. Phần V: Phân tích tình huống
    lines_V = raw_lines[sec_starts['V']+1 :]
    cs_blocks = []
    cur_cs = None
    for l in lines_V:
        m = re.match(r'^Câu\s+(\d+)[\s:：\.]*(.*)', l, re.IGNORECASE)
        if m:
            if cur_cs:
                cs_blocks.append(cur_cs)
            cur_cs = {'num': int(m.group(1)), 'q_lines': [m.group(2).strip()] if m.group(2).strip() else [], 'ans_lines': [], 'has_ans': False}
        elif cur_cs:
            if 'Đáp án tham khảo:' in l or 'Câu trả lời tham khảo:' in l:
                cur_cs['has_ans'] = True
                rest = l.replace('Đáp án tham khảo:', '').replace('Câu trả lời tham khảo:', '').strip()
                if rest:
                    cur_cs['ans_lines'].append(rest)
            elif cur_cs['has_ans']:
                cur_cs['ans_lines'].append(l)
            else:
                cur_cs['q_lines'].append(l)
    if cur_cs:
        cs_blocks.append(cur_cs)

    cs_questions = []
    for qb in cs_blocks:
        q_text = '\n'.join(qb['q_lines']).strip()
        cs_questions.append({
            'id': f"CS_{len(cs_questions)+1:03d}",
            'type': 'case_study',
            'section': 'Phần V: Phân tích tình huống',
            'question': clean_q_title(q_text),
            'answer': qb['ans_lines']
        })

    all_questions = sc_questions + mc_questions + tf_questions + sa_questions + cs_questions
    return {
        "title": "Ngân hàng câu hỏi xét thăng chức chuyền trưởng CESBG Việt Nam 2026",
        "total_questions": len(all_questions),
        "counts": {
            "single_choice": len(sc_questions),
            "multi_choice": len(mc_questions),
            "true_false": len(tf_questions),
            "short_answer": len(sa_questions),
            "case_study": len(cs_questions)
        },
        "questions": all_questions
    }


def generate_chuyen_truong_exam1(bank_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo Đề 1 chuẩn mẫu 60 câu / 100 điểm cho Chuyền Trưởng."""
    questions = bank_data.get("questions", [])
    sc = [dict(q) for q in questions if q.get("type") == "single_choice"][:30]
    mc = [dict(q) for q in questions if q.get("type") == "multi_choice"][:15]
    tf = [dict(q) for q in questions if q.get("type") == "true_false"][:10]
    sa = [dict(q) for q in questions if q.get("type") == "short_answer"][:4]
    cs = [dict(q) for q in questions if q.get("type") == "case_study"][:1]

    exam_q = []
    for idx, q in enumerate(sc + mc + tf + sa + cs, 1):
        q["num"] = idx
        if q.get("type") == "single_choice":
            q["points"] = 1.0
        elif q.get("type") == "multi_choice":
            q["points"] = 2.0
        elif q.get("type") == "true_false":
            q["points"] = 1.0
        elif q.get("type") == "short_answer":
            q["points"] = 5.0
        elif q.get("type") == "case_study":
            q["points"] = 10.0
        exam_q.append(q)

    return {
        "title": "Đề thi xét thăng chức chuyền trưởng CESBG Việt Nam (Đề 1)",
        "total_questions": len(exam_q),
        "questions": exam_q
    }


def main():
    base_dir = get_base_dir()
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 1. TRÍCH XUẤT ĐỀ TỔ TRƯỞNG (周边组长)
    to_truong_dir = data_dir / "to_truong"
    to_truong_dir.mkdir(exist_ok=True)
    
    goc_file = base_dir / "【周边组长题库】2026年CESBG越南厂区线组长考试 Gốc.docx"
    de1_file = base_dir / "【周边组长题库】2026年CESBG越南厂区线组长考试 1.docx"
    
    if goc_file.exists() and de1_file.exists():
        print(f"[*] [TỔ TRƯỞNG] Trích xuất dữ liệu từ Ngân hàng Gốc: {goc_file.name}...")
        bank_data_tt = extract_goc(str(goc_file))
        print(f"    - Tổng số câu: {bank_data_tt['total_questions']}")
        for k, v in bank_data_tt['counts'].items():
            print(f"      + {k}: {v} câu")
            
        print(f"[*] [TỔ TRƯỞNG] Trích xuất và ánh xạ đáp án Đề 1: {de1_file.name}...")
        de1_data_tt = extract_exam1(str(de1_file), bank_data_tt)
        validate_data(bank_data_tt, de1_data_tt)
        
        # Lưu vào data/to_truong/ và lưu mirror ở data/
        for p in [to_truong_dir / "question_bank.json", data_dir / "question_bank.json"]:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(bank_data_tt, f, ensure_ascii=False, indent=2)
        print(f"[✔] [TỔ TRƯỞNG] Đã lưu ngân hàng: {to_truong_dir / 'question_bank.json'}")
        
        for p in [to_truong_dir / "exam_de1.json", data_dir / "exam_de1.json"]:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(de1_data_tt, f, ensure_ascii=False, indent=2)
        print(f"[✔] [TỔ TRƯỞNG] Đã lưu Đề 1: {to_truong_dir / 'exam_de1.json'}")

    # 2. TRÍCH XUẤT ĐỀ CHUYỀN TRƯỞNG (线长)
    chuyen_truong_dir = data_dir / "chuyen_truong"
    chuyen_truong_dir.mkdir(exist_ok=True)
    
    ct_pdf_file = base_dir / "【线长题库】2026年CESBG越南厂区线组长考试 0418.pdf"
    if ct_pdf_file.exists():
        print(f"\n[*] [CHUYỀN TRƯỞNG] Trích xuất dữ liệu từ PDF: {ct_pdf_file.name}...")
        bank_data_ct = extract_chuyen_truong_pdf(str(ct_pdf_file))
        print(f"    - Tổng số câu: {bank_data_ct['total_questions']}")
        for k, v in bank_data_ct['counts'].items():
            print(f"      + {k}: {v} câu")
            
        ct_bank_path = chuyen_truong_dir / "question_bank.json"
        with open(ct_bank_path, "w", encoding="utf-8") as f:
            json.dump(bank_data_ct, f, ensure_ascii=False, indent=2)
        print(f"[✔] [CHUYỀN TRƯỞNG] Đã lưu ngân hàng: {ct_bank_path}")
        
        # Sinh Đề 1 chuẩn 60 câu / 100 điểm
        de1_data_ct = generate_chuyen_truong_exam1(bank_data_ct)
        ct_de1_path = chuyen_truong_dir / "exam_de1.json"
        with open(ct_de1_path, "w", encoding="utf-8") as f:
            json.dump(de1_data_ct, f, ensure_ascii=False, indent=2)
        print(f"[✔] [CHUYỀN TRƯỞNG] Đã lưu Đề 1 chuẩn mẫu: {ct_de1_path}")


if __name__ == '__main__':
    main()
