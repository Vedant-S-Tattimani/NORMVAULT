import os
import re
from typing import List, Optional, Tuple
from app.models.requirement import RequirementType, RequirementExtractionStatus
from app.schemas.extraction import (
    ProcurementExtractionSchema,
    ExtractedRequirementSchema,
    ExtractedParameterSchema,
)
from app.services.document_parser import NormalizedDocument, NormalizedBlock

class RequirementExtractorService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None
        else:
            self.client = None

    def extract_from_document(self, normalized_doc: NormalizedDocument) -> ProcurementExtractionSchema:
        """
        Extracts structured requirements from a normalized document.
        Uses OpenAI Structured Outputs if client is configured, otherwise a real deterministic extractor.
        All results undergo strict evidence alignment, offset resolution, parameter normalization, and deduplication.
        """
        if self.client:
            try:
                completion = self.client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a procurement technical specifications analyst. "
                                "Extract atomic technical requirements from the document. "
                                "Do NOT hallucinate requirements or standards not present in the text. "
                                "Mark EXPLICIT for definitive clauses with numeric/standard constraints. "
                                "Mark INFERRED for logical consequences. "
                                "Mark UNCERTAIN for ambiguous or qualitative statements (e.g. 'suitable for harsh environments' must remain UNCERTAIN without guessing IP ratings). "
                                "Provide verbatim source_text as evidence."
                            ),
                        },
                        {"role": "user", "content": f"Extract requirements from:\n\n{normalized_doc.full_text}"},
                    ],
                    response_format=ProcurementExtractionSchema,
                )
                parsed = completion.choices[0].message.parsed
            except Exception:
                parsed = self._deterministic_extract(normalized_doc)
        else:
            parsed = self._fallback_extract(normalized_doc)

        return self._validate_and_align_extraction(parsed, normalized_doc)

    def _fallback_extract(self, normalized_doc: NormalizedDocument) -> ProcurementExtractionSchema:
        return self._deterministic_extract(normalized_doc)


    def _validate_and_align_extraction(
        self, parsed: ProcurementExtractionSchema, normalized_doc: NormalizedDocument
    ) -> ProcurementExtractionSchema:
        """
        Post-extraction validation pipeline:
        1. Verifies verbatim occurrence of source_text in document.
        2. Assigns exact start_offset, end_offset, page_number, and block_identifier.
        3. Rejects hallucinated evidence and downgrades unsupported claims to UNCERTAIN.
        4. Enforces ambiguity rules (no guessing explicit ratings from vague phrases).
        5. Deduplicates requirements with identical content.
        """
        full_text = normalized_doc.full_text
        validated_reqs: List[ExtractedRequirementSchema] = []
        seen_keys = set()

        for req in parsed.requirements:
            evidence_valid = False
            start_off = req.start_offset
            end_off = req.end_offset
            matched_block: Optional[NormalizedBlock] = None

            # Evidence Verification
            if req.source_text:
                cleaned_evidence = req.source_text.strip()
                match_pos = -1
                if (
                    req.start_offset is not None
                    and 0 <= req.start_offset < len(full_text)
                    and full_text[req.start_offset:req.start_offset + len(cleaned_evidence)] == cleaned_evidence
                ):
                    match_pos = req.start_offset
                else:
                    match_pos = full_text.find(cleaned_evidence)

                if match_pos != -1:
                    evidence_valid = True
                    start_off = match_pos
                    end_off = match_pos + len(cleaned_evidence)
                    # Associate with block and page
                    for block in normalized_doc.blocks:
                        if block.start_offset is not None and block.end_offset is not None:
                            if block.start_offset <= start_off < block.end_offset:
                                matched_block = block
                                break
                        elif cleaned_evidence in block.text:
                            matched_block = block
                            break
                else:
                    # Hallucinated or mutated evidence - reject evidence
                    evidence_valid = False
                    req.source_text = None
                    start_off = None
                    end_off = None
                    if req.extraction_status == RequirementExtractionStatus.EXPLICIT:
                        req.extraction_status = RequirementExtractionStatus.UNCERTAIN

            if not evidence_valid:
                req.source_text = None
                start_off = None
                end_off = None

            req.start_offset = start_off
            req.end_offset = end_off

            if matched_block:
                if req.page_number is None:
                    req.page_number = matched_block.page_number
                if req.section_heading is None:
                    req.section_heading = matched_block.section_heading
                if req.block_identifier is None:
                    req.block_identifier = matched_block.block_id

            # Ambiguity guard: If extracted text is vague without specific parameters, ensure not EXPLICIT
            vague_indicators = ["suitable for", "adequate", "as required", "harsh environment", "good quality"]
            if any(v in req.extracted_text.lower() for v in vague_indicators) and not req.parameters:
                req.extraction_status = RequirementExtractionStatus.UNCERTAIN

            # Ensure all parameters have normalized/original values
            for param in req.parameters:
                if not param.original_value and param.target_value:
                    param.original_value = param.target_value
                if not param.normalized_value and param.target_value:
                    param.normalized_value = param.target_value
                if not param.target_value:
                    param.target_value = param.normalized_value or param.original_value or ""

            # Deduplication key: normalized text + evidence offset
            dedup_key = (
                re.sub(r'\s+', ' ', req.extracted_text.lower().strip()),
                start_off,
                req.requirement_type
            )
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            validated_reqs.append(req)

        parsed.requirements = validated_reqs
        return parsed

    def _deterministic_extract(self, normalized_doc: NormalizedDocument) -> ProcurementExtractionSchema:
        """
        General-purpose deterministic specification clause and parameter extraction engine.
        Parses sentences, identifies specification requirements, extracts technical parameters,
        computes character spans, and determines appropriate types and statuses.
        """
        requirements: List[ExtractedRequirementSchema] = []
        full_text = normalized_doc.full_text

        # Heuristic for specification title and product name
        title = "Procurement Specification"
        target_product = "Equipment"

        for block in normalized_doc.blocks:
            if block.section_heading:
                title = block.section_heading
                break

        # Process each block
        for block in normalized_doc.blocks:
            # Segment block into sentences
            raw_sentences = re.split(r'(?<=[.!?])\s+', block.text)
            
            for raw_sent in raw_sentences:
                sent = raw_sent.strip()
                if not sent or len(sent) < 5:
                    continue

                # Locate sentence in full_text
                sent_offset = full_text.find(sent, block.start_offset if block.start_offset is not None else 0)
                if sent_offset == -1:
                    sent_offset = full_text.find(sent)

                start_offset = sent_offset if sent_offset != -1 else None
                end_offset = (sent_offset + len(sent)) if sent_offset != -1 else None

                # Extract technical parameters
                parameters = self._extract_parameters(sent)

                # Determine if this sentence represents a specification requirement
                is_requirement, req_type, status, summary = self._analyze_sentence(sent, parameters)

                if is_requirement:
                    requirements.append(
                        ExtractedRequirementSchema(
                            requirement_type=req_type,
                            extraction_status=status,
                            extracted_text=summary,
                            source_text=sent,
                            page_number=block.page_number,
                            section_heading=block.section_heading,
                            block_identifier=block.block_id,
                            start_offset=start_offset,
                            end_offset=end_offset,
                            parameters=parameters,
                        )
                    )

        # Fallback if no specific requirements matched
        if not requirements and normalized_doc.blocks:
            first_block = normalized_doc.blocks[0]
            first_sent = first_block.text.split(".")[0].strip()
            if first_sent:
                first_sent += "."
                requirements.append(
                    ExtractedRequirementSchema(
                        requirement_type=RequirementType.MATERIAL,
                        extraction_status=RequirementExtractionStatus.UNCERTAIN,
                        extracted_text=first_sent,
                        source_text=first_sent if first_sent in full_text else None,
                        page_number=first_block.page_number,
                        section_heading=first_block.section_heading,
                        block_identifier=first_block.block_id,
                        start_offset=full_text.find(first_sent) if first_sent in full_text else None,
                        end_offset=(full_text.find(first_sent) + len(first_sent)) if first_sent in full_text else None,
                        parameters=[],
                    )
                )

        # Infer target product from requirements or text
        for r in requirements:
            if "motor" in r.extracted_text.lower() or "motor" in (r.source_text or "").lower():
                target_product = "Electric Motor"
                break
            elif "pipe" in r.extracted_text.lower():
                target_product = "Pipes & Fittings"
                break

        return ProcurementExtractionSchema(
            title=title,
            target_product_name=target_product,
            requirements=requirements,
        )

    def _analyze_sentence(
        self, sentence: str, parameters: List[ExtractedParameterSchema]
    ) -> Tuple[bool, RequirementType, RequirementExtractionStatus, str]:
        """
        Analyzes a sentence to determine requirement classification, status, and concise summary.
        """
        lower = sentence.lower()

        # Modal verbs and requirement cues
        has_modal = any(w in lower for w in ["shall", "must", "required to", "should", "needs to", "conforming to", "complies with"])
        has_params = len(parameters) > 0
        has_spec_word = any(w in lower for w in ["rating", "enclosure", "temperature", "pressure", "dimensions", "grade", "supply", "capacity", "coating", "tolerance", "suitable for", "standard", "is "])

        if not (has_modal or has_params or has_spec_word):
            return False, RequirementType.MATERIAL, RequirementExtractionStatus.EXPLICIT, sentence

        # Determine RequirementType
        req_type = RequirementType.MATERIAL
        if any(w in lower for w in ["dimension", "length", "width", "height", "thickness", "diameter", "mm", "cm", " × ", " x "]):
            req_type = RequirementType.DIMENSIONAL
        elif any(w in lower for w in ["power", "kw", "hp", "motor", "torque", "speed", "rpm", "bearing"]):
            req_type = RequirementType.MECHANICAL
        elif any(w in lower for w in ["pressure", "bar", "mpa", "kpa", "psi", "pump", "valve"]):
            req_type = RequirementType.MECHANICAL
        elif any(w in lower for w in ["ip55", "ip65", "ip67", "ip68", "enclosure", "protection", "safety", "fire", "flame"]):
            req_type = RequirementType.SAFETY
        elif any(w in lower for w in ["test", "hydrostatic", "sampling", "inspection", "laboratory"]):
            req_type = RequirementType.TESTING
        elif any(w in lower for w in ["bis", "isi mark", "qco", "certified", "standard", "is 4984", "is 325"]):
            req_type = RequirementType.CERTIFICATION
        elif any(w in lower for w in ["temperature", "thermal", "degree", "°c"]):
            req_type = RequirementType.MECHANICAL
        elif any(w in lower for w in ["chemical", "corrosion", "purity", "acid"]):
            req_type = RequirementType.CHEMICAL

        # Determine ExtractionStatus
        if any(w in lower for w in ["suitable for", "harsh environment", "adequate", "general purpose"]):
            # Descriptive without hard parameter
            if not parameters and not ("shall" in lower or "must" in lower):
                status = RequirementExtractionStatus.UNCERTAIN
            else:
                status = RequirementExtractionStatus.EXPLICIT if ("shall" in lower or "must" in lower or parameters) else RequirementExtractionStatus.INFERRED
        elif has_modal or parameters:
            status = RequirementExtractionStatus.EXPLICIT
        else:
            status = RequirementExtractionStatus.INFERRED

        # Clean summary: remove leading "The " or clean up trailing period
        summary = sentence.strip()
        if summary.startswith("The ") and len(summary) > 4:
            summary = summary[4:]
        if not summary.endswith("."):
            summary += "."

        return True, req_type, status, summary

    def _extract_parameters(self, text: str) -> List[ExtractedParameterSchema]:
        """
        Extracts structured technical parameters from text preserving:
        original value, normalized value, unit, and operator/range.
        Supports:
        - Ingress Protection: IP55, IP65, IP68
        - Dimensions: 1000 mm × 500 mm, 50 mm x 25 mm
        - Temperature ranges: -10 °C to 50 °C
        - Pressure ranges: 10–15 bar, 10 to 15 bar
        - Single values: 5 kW, 16 MPa, 230 V, 50 Hz
        """
        params: List[ExtractedParameterSchema] = []

        # 1. Ingress Protection (e.g. IP55, IP67)
        ip_match = re.search(r'\b(IP\s*[0-9]{2}[A-Z]?)\b', text, re.IGNORECASE)
        if ip_match:
            raw_ip = ip_match.group(1).upper().replace(" ", "")
            params.append(
                ExtractedParameterSchema(
                    name="Ingress Protection",
                    original_value=ip_match.group(1),
                    normalized_value=raw_ip,
                    target_value=raw_ip,
                    unit=None,
                    operator="=",
                )
            )

        # 2. Dimensions (e.g. 1000 mm × 500 mm or 1000 mm x 500 mm or 1000x500 mm)
        dim_match = re.search(
            r'([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|m)?\s*[×xX]\s*([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|m)\b',
            text,
        )
        if dim_match:
            val1 = dim_match.group(1)
            val2 = dim_match.group(3)
            unit = dim_match.group(4)
            orig = dim_match.group(0)
            norm = f"{val1} x {val2}"
            params.append(
                ExtractedParameterSchema(
                    name="Dimensions",
                    original_value=orig,
                    normalized_value=norm,
                    target_value=norm,
                    unit=unit,
                    operator="DIMENSIONS",
                )
            )

        # 3. Ranges (e.g. -10 °C to 50 °C, 10–15 bar, 10 to 20 mm)
        range_match = re.search(
            r'(-?[0-9]+(?:\.[0-9]+)?)\s*(°C|C|bar|MPa|kPa|psi|kW|V|A|Hz|mm|cm|m)?\s*(?:to|–|—|-)\s*(-?[0-9]+(?:\.[0-9]+)?)\s*(°C|C|bar|MPa|kPa|psi|kW|V|A|Hz|mm|cm|m)\b',
            text,
        )
        if range_match:
            min_val = range_match.group(1)
            unit1 = range_match.group(2)
            max_val = range_match.group(3)
            unit2 = range_match.group(4)
            unit = unit2 if unit2 else unit1
            orig = range_match.group(0)
            norm = f"{min_val} to {max_val}"
            
            # Param name heuristic
            p_name = "Parameter Range"
            if unit in ["°C", "C"]:
                p_name = "Operating Temperature"
            elif unit in ["bar", "MPa", "kPa", "psi"]:
                p_name = "Pressure Range"
            elif unit in ["kW", "W", "HP"]:
                p_name = "Power Range"
            elif unit in ["mm", "cm", "m"]:
                p_name = "Dimensional Range"

            params.append(
                ExtractedParameterSchema(
                    name=p_name,
                    original_value=orig,
                    normalized_value=norm,
                    target_value=norm,
                    unit=unit,
                    operator="RANGE",
                )
            )

        # 4. Single Value + Unit (e.g. 5 kW, 16 MPa, >= 415 MPa)
        # Avoid matching numbers already consumed in ranges or dimensions
        single_matches = re.finditer(
            r'(>=|<=|>|<|=|min\.?|max\.?)?\s*(-?[0-9]+(?:\.[0-9]+)?)\s*(kW|HP|bar|MPa|kPa|psi|°C|mm|cm|m|kg|RPM|V|Hz)\b',
            text,
        )
        for sm in single_matches:
            full_str = sm.group(0).strip()
            # Check if this substring was already part of a range or dimension
            already_covered = any(full_str in p.original_value for p in params)
            if not already_covered:
                op = sm.group(1) or "="
                val = sm.group(2)
                unit = sm.group(3)
                p_name = "Technical Parameter"
                if unit in ["kW", "HP"]:
                    p_name = "Rated Power"
                elif unit in ["bar", "MPa", "kPa", "psi"]:
                    p_name = "Pressure"
                elif unit in ["V"]:
                    p_name = "Voltage"
                elif unit in ["Hz"]:
                    p_name = "Frequency"
                elif unit in ["RPM"]:
                    p_name = "Rated Speed"
                elif unit in ["mm", "cm", "m"]:
                    p_name = "Dimension"

                params.append(
                    ExtractedParameterSchema(
                        name=p_name,
                        original_value=full_str,
                        normalized_value=val,
                        target_value=val,
                        unit=unit,
                        operator=op,
                    )
                )

        return params

