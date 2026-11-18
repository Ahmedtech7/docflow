
# استيراد أدوات التعامل مع JSON والملفات
import json       # تحويل بيانات Python إلى JSON
import os         # استبدال الملف النهائي بشكل آمن
import tempfile   # إنشاء ملف مؤقت أثناء الحفظ
from pathlib import Path  # التعامل مع مسارات الملفات

# استيراد الدوال القديمة من Task 1.1 و Task 1.2
from inventory import (
    count_by,             # حساب المستندات حسب النوع أو القسم
    validate_inventory    # فحص المستندات وتحديد المقبول والمرفوض
)


# كلاس مسؤول عن بناء تقارير الجرد والتحقق
class ReportBuilder:

    # بناء تقرير الجرد
    def inventory_report(self, documents):
        # افحص المستندات باستخدام دالة Task 1.2 القديمة
        accepted, rejected = validate_inventory(documents)

        # أعد تقريرًا يوضح عدد السجلات الأصلية والمقبولة والمرفوضة
        return {
            "summary": {
                "total_records": len(documents),
                "accepted_documents": len(accepted),
                "rejected_documents": len(rejected)
            },

            # احسب المستندات المقبولة فقط
            # حتى لا تتعطل الإحصاءات بسبب بيانات غير صحيحة
            "by_type": count_by(accepted, "document_type"),
            "by_department": count_by(accepted, "department")
        }

    # بناء تقرير التحقق
    def validation_report(self, documents):
        # إعادة استخدام دالة الفحص الموجودة في Task 1.2
        accepted, rejected = validate_inventory(documents)

        # قائمة لتجميع تفاصيل المستندات المرفوضة
        rejected_records = []

        # مر على كل مستند مرفوض
        for index, doc_id, errors in rejected:
            # احصل على المستند الأصلي من القائمة
            document = documents[index]

            # ابدأ بمعرف فارغ إذا لم يكن موجودًا
            original_id = None

            # خذ المعرف الأصلي إذا كان المستند Dictionary
            if isinstance(document, dict):
                original_id = document.get("id")

            # أضف تفاصيل المستند المرفوض إلى التقرير
            rejected_records.append({
                "index": index,
                "id": original_id,
                "reasons": errors
            })

        # أرجع تقرير التحقق مع عدد المستندات الأصلية والمقبولة والمرفوضة
        return {
            "summary": {
                "total_records": len(documents),
                "accepted_documents": len(accepted),
                "rejected_documents": len(rejected)
            },

            # احسب الأنواع والأقسام للمستندات المقبولة فقط
            "by_type": count_by(accepted, "document_type"),
            "by_department": count_by(accepted, "department"),

            # احتفظ بتفاصيل كل مستند مرفوض وأسباب رفضه
            "rejected": rejected_records
        }


# كلاس مسؤول عن حفظ التقارير بصيغة JSON
class ReportWriter:

    def save(self, report, input_path, output_path):
        # تحويل مسارات الإدخال والإخراج إلى مسارات كاملة
        source = Path(input_path).resolve()
        destination = Path(output_path).resolve()

        # منع الكتابة فوق ملف البيانات الأصلي
        if source == destination:
            raise ValueError(
                "Cannot overwrite the input JSON file"
            )

        # تأكد أن مكان الإخراج ليس مجلدًا
        if destination.exists() and destination.is_dir():
            raise ValueError(
                "Output path must be a file"
            )

        # جهز بيانات التقرير كنص JSON قبل بدء الكتابة
        content = json.dumps(
            report,
            indent=2,           # تنسيق النص بمسافتين
            ensure_ascii=False, # دعم الأحرف العربية
            sort_keys=True,     # ترتيب المفاتيح
            allow_nan=False     # منع القيم الرقمية غير الصالحة
        )

        # إنشاء مجلد التقارير إذا لم يكن موجودًا
        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # استخدم ملفًا مؤقتًا لحماية التقرير من الكتابة الناقصة
        temporary_path = None

        try:
            # إنشاء الملف المؤقت داخل مجلد الإخراج
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=".docflow_",
                suffix=".tmp",
                delete=False
            ) as file:
                temporary_path = Path(file.name)

                # كتابة محتوى التقرير في الملف المؤقت
                file.write(content)
                file.write("\n")

            # استبدال التقرير النهائي بعد اكتمال الكتابة
            os.replace(temporary_path, destination)

        finally:
            # تنظيف الملف المؤقت إن بقي بعد نجاح أو فشل الحفظ
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        # عرض مكان التقرير بعد نجاح الحفظ
        print(f"Report saved to: {destination}")
