# Lossless source representation

The owner’s explicit lossless/raw preservation rule governs the four accepted-source explanatory texts below. The accepted DDL requires UNKNOWN to have no typed value payload. Each source text remains exact UTF-8 in wa_meta.legacy_row.original_columns.value_text, with row digest and source identity. The assertion retains value_kind UNKNOWN and initial CANDIDATE standing. Its normalized value_text is absent; assertion metadata records FORENSIC_ONLY_EXPLANATORY_TEXT_WHEN_VALUE_KIND_UNKNOWN. This is an explicitly documented projection, not a source conversion, scientific repair, filtering, or admission. No DDL constraint is relaxed. The earlier ETL recipe’s assumption that the accepted baseline has no such explanatory text was false; the owner’s subsequent explicit raw-only disposition instruction applies.

- R_HYDRA_INTERIOR_UNKNOWN: 'UNKNOWN: available mass/shape data do not justify detailed interior layering or unique bulk composition'
- R_KERBEROS_INTERIOR_UNKNOWN: 'UNKNOWN: available mass/shape data do not justify detailed interior layering or unique bulk composition'
- R_NIX_INTERIOR_UNKNOWN: 'UNKNOWN: available mass/shape data do not justify detailed interior layering or unique bulk composition'
- R_STYX_INTERIOR_UNKNOWN: 'UNKNOWN: available mass/shape data do not justify detailed interior layering or unique bulk composition'
