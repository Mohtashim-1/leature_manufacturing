# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class HideGrading(Document):
	def validate(self):
		import frappe

		score = 0
		reject = False
		for row in self.defects or []:
			sev = {"Low": 1, "Medium": 3, "High": 6}.get(row.severity or "Low", 1)
			score += (row.count or 1) * sev
			if row.defect_type in ("Putrefaction",) and (row.severity or "") == "High":
				reject = True
		if reject or score >= 40:
			code = "Reject"
		elif score >= 25:
			code = "D"
		elif score >= 15:
			code = "C"
		elif score >= 6:
			code = "B"
		else:
			code = "A"
		if frappe.db.exists("Leather Grade", code):
			self.recommended_grade = code
		if not self.final_grade:
			self.final_grade = self.recommended_grade
		for row in self.grade_summary or []:
			row.amount = (row.pieces or 0) * (row.rate or 0)
