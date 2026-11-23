
# نستورد مكتبة json الموجودة في Python
# نحتاجها لقراءة ملفات JSON وتحويلها إلى بيانات Python
import json

# نستورد argparse حتى نستقبل أوامر المستخدم من التيرمنال
# مثل --validate و --output
import argparse

# نستورد sys حتى نقدر نطبع الأخطاء وننهي البرنامج برمز خطأ
import sys

# نستورد datetime عشان نفحص صيغة التاريخ والوقت
from datetime import datetime

# نستورد PurePosixPath عشان نتعامل مع امتداد اسم الملف
# مثل .txt أو .md
from pathlib import PurePosixPath


# ==========================================================
# Task 1.1 - قراءة المستندات وحساب أعدادها
# ==========================================================


# نعرّف دالة اسمها load_inventory
# كلمة def معناها أننا نعرّف دالة جديدة
# المتغير path هو مسار ملف JSON الذي نريد قراءته
def load_inventory(path):

    # افتح الملف الموجود في المسار path
    # "r" معناها وضع القراءة Read
    # encoding="utf-8" يعني استخدام ترميز يدعم العربية
    # كلمة with تغلق الملف تلقائيًا بعد الانتهاء منه
    with open(path, "r", encoding="utf-8") as file:

        # json.load تقرأ محتوى ملف JSON
        # وتحوله إلى قائمة أو قاموس حسب محتواه
        # نخزن النتيجة في متغير اسمه documents
        documents = json.load(file)

    # isinstance تفحص نوع البيانات
    # نتأكد أن documents من نوع list
    # not معناها عكس الشرط
    if not isinstance(documents, list):

        # إذا لم تكن البيانات قائمة، نرفع خطأ
        # لأن مشروعنا يتوقع قائمة مستندات
        raise ValueError("JSON must contain an array")

    # نرجع قائمة المستندات لمن استدعى الدالة
    return documents


# هذه الدالة تحسب عدد المستندات حسب حقل معين
# documents = قائمة المستندات
# key = اسم الحقل الذي نريد العد بناءً عليه
# مثال: document_type أو department
def count_by(documents, key):

    # ننشئ قاموسًا فارغًا لتخزين نتائج العد
    # القاموس Dictionary يخزن البيانات بشكل مفتاح وقيمة
    counts = {}

    # حلقة for تمر على كل مستند داخل قائمة documents
    # في كل دورة، المتغير document يمثل مستندًا واحدًا
    for index, document in enumerate(documents):

        # نقرأ قيمة الحقل المطلوب من المستند الحالي
        # مثال: إذا key = "department" فقد تكون value = "HR"
        # Task 2.1 (Bug C): سجل ناقص أو غير نصي كان يسبب KeyError/TypeError غامضًا
        # السياسة: نتوقف بخطأ واضح يحدد رقم السجل بدل عرض إجماليات مضللة
        value = document.get(key) if isinstance(document, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Record at index {index} has a missing or non-string "
                f"'{key}'. Fix the record, or run with --validate to "
                f"list all invalid records."
            )

        # counts.get(value, 0) تبحث عن عدد هذه القيمة
        # إذا لم تكن موجودة، تبدأ من صفر
        # ثم نضيف 1 لأننا وجدنا مستندًا جديدًا بهذه القيمة
        counts[value] = counts.get(value, 0) + 1

    # نرجع قاموس الأعداد بعد الانتهاء من جميع المستندات
    return counts


# هذه الدالة تعرض ملخص الجرد في التيرمنال
def show_inventory(documents):

    # نستخدم الدالة القديمة count_by لحساب أنواع المستندات
    types = count_by(documents, "document_type")

    # نستخدم نفس الدالة لحساب المستندات حسب القسم
    departments = count_by(documents, "department")

    # print تطبع نصًا في التيرمنال
    print("DocFlow - Document Inventory")

    # len تحسب عدد العناصر داخل القائمة
    print("Total documents:", len(documents))

    # \n معناها سطر جديد قبل النص
    print("\nBy type:")

    # sorted ترتب أسماء الأنواع أبجديًا
    # حلقة for تمر على كل نوع وتطبع عدده
    for name in sorted(types):

        # f-string تسمح لنا بوضع متغيرات داخل النص
        # types[name] تجلب العدد الخاص بهذا النوع
        print(f"  {name}: {types[name]}")

    # اطبع عنوان الأقسام
    print("\nBy department:")

    # مر على الأقسام بالترتيب الأبجدي
    for name in sorted(departments):

        # اطبع اسم القسم وعدد مستنداته
        print(f"  {name}: {departments[name]}")


# ==========================================================
# Task 1.2 - التحقق من صحة بيانات المستندات
# ==========================================================


# هذه الدالة تفحص مستندًا واحدًا فقط
# وترجع قائمة بالأخطاء الموجودة فيه
def validate_document(document):

    # ننشئ قائمة فارغة لتجميع رسائل الأخطاء
    errors = []

    # نتأكد أولًا أن المستند عبارة عن Dictionary
    # لأننا نتوقع حقولًا مثل id و filename
    if not isinstance(document, dict):

        # إذا لم يكن قاموسًا، نرجع الخطأ مباشرة
        return ["Document must be an object"]

    # أسماء الحقول التي يجب أن تحتوي نصوصًا
    text_fields = [
        "id",
        "filename",
        "department",
        "document_type",
        "uploaded_at",
        "file_path"
    ]

    # نضيف size_kb إلى قائمة الحقول المطلوبة
    # لأن الحجم مطلوب لكنه ليس نصًا
    required_fields = text_fields + ["size_kb"]

    # نمر على جميع الحقول المطلوبة
    for field in required_fields:

        # إذا كان الحقل غير موجود في المستند
        if field not in document:

            # نضيف رسالة الخطأ إلى قائمة errors
            # append معناها إضافة عنصر إلى نهاية القائمة
            errors.append(f"Missing field: {field}")

    # نفحص الحقول النصية واحدة واحدة
    for field in text_fields:

        # نفحص قيمة الحقل فقط إذا كان موجودًا
        if field in document:

            # نأخذ قيمة الحقل
            value = document[field]

            # الشرط الأول: هل القيمة ليست نصًا؟
            # الشرط الثاني: هل النص فارغ بعد إزالة المسافات؟
            # strip تزيل المسافات من بداية النص ونهايته
            if not isinstance(value, str) or not value.strip():

                # أضف رسالة خطأ إذا كانت القيمة غير صحيحة
                errors.append(f"Invalid or blank field: {field}")

    # ------------------------------------------------------
    # فحص نوع المستند
    # ------------------------------------------------------

    # get تجلب قيمة document_type
    # إذا لم يكن المفتاح موجودًا ترجع None بدل إظهار خطأ
    doc_type = document.get("document_type")

    # نتأكد أن نوع المستند نص وليس فارغًا
    if isinstance(doc_type, str) and doc_type.strip():

        # نسمح فقط بنوعي txt و md
        if doc_type not in ("txt", "md"):

            # إذا كان النوع مختلفًا نضيف سبب الرفض
            errors.append(f"Unsupported document type: {doc_type}")

    # ------------------------------------------------------
    # فحص اسم الملف وامتداده
    # ------------------------------------------------------

    # اجلب اسم الملف من المستند
    filename = document.get("filename")

    # نفحص الاسم إذا كان نصًا غير فارغ
    if isinstance(filename, str) and filename.strip():

        # اسم الملف يجب ألا يحتوي على / أو \
        # لأننا نريد اسم ملف وليس مسارًا كاملًا
        if "/" in filename or "\\" in filename:
            errors.append("Invalid filename")

        # suffix ترجع امتداد اسم الملف
        # مثال: report.txt -> .txt
        extension = PurePosixPath(filename).suffix

        # هل امتداد الملف من الأنواع المسموحة؟
        if extension not in (".txt", ".md"):
            errors.append("Unsupported filename extension")

        # إذا كان نوع المستند نفسه صحيحًا
        if doc_type in ("txt", "md"):

            # لازم الامتداد يطابق نوع المستند
            # مثال: النوع txt يعني الامتداد لازم يكون .txt
            if extension != "." + doc_type:

                # أضف خطأ إذا النوع والامتداد مختلفان
                errors.append(
                    "Filename extension does not match document type"
                )

    # ------------------------------------------------------
    # فحص حجم المستند
    # ------------------------------------------------------

    # نفحص الحجم فقط إذا كان الحقل موجودًا
    if "size_kb" in document:

        # خذ قيمة الحجم
        size = document["size_kb"]

        # type ترجع نوع البيانات
        # نسمح فقط بالأعداد الصحيحة int والعشرية float
        # استخدام type بدل isinstance يمنع قبول True كأنه رقم
        if type(size) not in (int, float):

            errors.append("Size must be a number")

        # يجب أن يكون الحجم أكبر من صفر
        # وألا يتجاوز 5120 كيلوبايت
        elif not 0 < size <= 5120:

            errors.append("Size must be between 0 and 5120 KB")

    # ------------------------------------------------------
    # فحص تاريخ رفع المستند
    # ------------------------------------------------------

    # خذ تاريخ الرفع
    uploaded_at = document.get("uploaded_at")

    # افحص التاريخ فقط إذا كان نصًا غير فارغ
    if isinstance(uploaded_at, str) and uploaded_at.strip():

        # try تعني حاول تنفيذ الكود
        # إذا كانت صيغة التاريخ خاطئة سينتقل البرنامج إلى except
        try:

            # صيغة التاريخ المطلوبة تحتوي T بين التاريخ والوقت
            # مثال: 2026-01-10T10:30:00
            if "T" not in uploaded_at:

                # نرفع خطأ إذا لم يوجد T
                raise ValueError("Missing time")

            # هذه الدالة تحاول تحويل النص إلى تاريخ ووقت
            # إذا لم تكن الصيغة صحيحة سترفع ValueError
            datetime.fromisoformat(uploaded_at)

        # التعامل مع خطأ صيغة التاريخ
        except ValueError:

            # أضف السبب إلى قائمة الأخطاء بدل إيقاف فحص المستند
            errors.append("Invalid ISO 8601 date-time")

    # ------------------------------------------------------
    # فحص مسار المستند
    # ------------------------------------------------------

    # خذ مسار المستند من بياناته
    file_path = document.get("file_path")

    # تأكد أن المسار نص غير فارغ
    if isinstance(file_path, str) and file_path.strip():

        # split تقسم النص عند علامة /
        # مثال:
        # data/documents/report.txt
        # تصبح ["data", "documents", "report.txt"]
        parts = file_path.split("/")

        # نرفض المسار إذا تحقق أي شرط غير آمن
        if (
            # نرفض استخدام الشرطة العكسية
            "\\" in file_path

            # نرفض .. لأنها قد تشير إلى المجلد الأب
            or ".." in parts

            # يجب أن يبدأ المسار بـ data/documents
            or parts[:2] != ["data", "documents"]

            # يجب وجود اسم ملف بعد اسم المجلد
            or len(parts) < 3

            # يجب ألا يكون آخر جزء فارغًا
            or not parts[-1]

            # نرفض المسارات المطلقة التي تبدأ بـ /
            or file_path.startswith("/")

            # نرفض وجود : في أول جزء من المسار
            or ":" in parts[0]
        ):

            # أضف خطأ إذا كان المسار غير صالح
            errors.append("Invalid file path")

    # نرجع جميع الأخطاء الموجودة في المستند
    # إذا كانت القائمة فارغة، فهذا يعني أن المستند اجتاز الفحص
    return errors


# هذه الدالة تفحص جميع المستندات
# وترجع قائمتين: المقبولين والمرفوضين
def validate_inventory(documents):

    # قائمة المستندات الصحيحة
    accepted = []

    # قائمة المستندات التي تحتوي أخطاء
    rejected = []

    # set مجموعة لتخزين معرفات المستندات المقبولة
    # نستخدمها لاكتشاف تكرار الـ ID
    accepted_ids = set()

    # enumerate تعطينا موقع المستند والمستند نفسه
    # index يبدأ من صفر
    for index, document in enumerate(documents):

        # افحص المستند الحالي باستخدام الدالة السابقة
        errors = validate_document(document)

        # نبدأ بدون معرف
        doc_id = None

        # اقرأ المعرف إذا كان المستند قاموسًا
        if isinstance(document, dict):

            # get تحاول جلب قيمة id
            value = document.get("id")

            # تأكد أن المعرف نص وغير فارغ
            if isinstance(value, str) and value.strip():

                # strip تزيل المسافات الخارجية
                # lower تحول الأحرف الإنجليزية إلى صغيرة
                # هذا يساعدنا نعتبر DOC-001 و doc-001 متكررين
                doc_id = value.strip().lower()

                # إذا كان المعرف موجودًا في المقبولين سابقًا
                if doc_id in accepted_ids:

                    # أضف خطأ التكرار
                    errors.append("Duplicate document ID")

        # إذا كانت قائمة الأخطاء تحتوي على أي عنصر
        if errors:

            # أضف المستند إلى قائمة المرفوضين
            # نخزن رقم موقعه ومعرفه وجميع الأخطاء
            rejected.append((index, doc_id, errors))

        else:

            # إذا لم توجد أخطاء نضيف المستند إلى المقبولين
            accepted.append(document)

            # ونحفظ معرفه لكي نكتشف تكراره لاحقًا
            accepted_ids.add(doc_id)

    # نرجع القائمتين معًا
    # يمكن استقبالها هكذا:
    # accepted, rejected = validate_inventory(documents)
    return accepted, rejected


# هذه الدالة تطبع نتائج التحقق في التيرمنال
def show_validation(documents):

    # نفحص المستندات ونستقبل القائمتين
    accepted, rejected = validate_inventory(documents)

    # عنوان النتيجة
    print("DocFlow - Document Validation")

    # len تحسب عدد المستندات في كل قائمة
    print("Documents inspected:", len(documents))
    print("Accepted:", len(accepted))
    print("Rejected:", len(rejected))

    # مر على كل مستند مرفوض
    for index, doc_id, errors in rejected:

        # اطبع موقع المستند ومعرفه
        # إذا لم يوجد معرف نعرض Unknown
        print(
            f"\nRejected record at index {index} "
            f"({doc_id or 'Unknown'}):"
        )

        # اطبع جميع أسباب الرفض واحدًا واحدًا
        for error in errors:
            print(f"- {error}")


# ==========================================================
# Task 1.3 - استقبال أوامر التشغيل وتصدير التقارير
# ==========================================================


# هذه هي دالة التشغيل الرئيسية الوحيدة في البرنامج
def main():

    # أنشئ Parser لقراءة الخيارات من التيرمنال
    parser = argparse.ArgumentParser(
        description="DocFlow Inventory and Reporting CLI"
    )

    # أضف وسيطًا مطلوبًا يمثل مسار ملف JSON
    parser.add_argument(
        "file_path",
        help="Path to JSON file"
    )

    # خيار --validate
    # إذا كتبه المستخدم تصبح args.validate = True
    # وإذا لم يكتبه تصبح False
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate document metadata"
    )

    # خيار --output
    # يسمح للمستخدم بتحديد مكان حفظ تقرير JSON
    # إذا لم يُكتب تكون args.output = None
    parser.add_argument(
        "--output",
        help="Save report as JSON"
    )

    # parse_args تقرأ الأمر المكتوب في التيرمنال
    # وتخزن القيم داخل المتغير args
    args = parser.parse_args()

    # حاول تشغيل البرنامج
    # إذا حدث خطأ متوقع سنعالجه في except
    try:

        # اقرأ الملف باستخدام دالتنا القديمة من Task 1.1
        documents = load_inventory(args.file_path)

        # إذا كتب المستخدم --output نريد حفظ تقرير
        if args.output:

            # استورد كلاسات التقارير من reporting.py
            # وضعنا الاستيراد هنا حتى لا يحدث استيراد دائري
            # أثناء تشغيل inventory.py
            from reporting import ReportBuilder, ReportWriter

            # أنشئ كائنًا من كلاس بناء التقارير
            builder = ReportBuilder()

            # أنشئ كائنًا من كلاس حفظ التقارير
            writer = ReportWriter()

            # إذا كتب المستخدم --validate
            if args.validate:

                # ابنِ تقرير التحقق الذي يوضح المقبول والمرفوض
                report = builder.validation_report(documents)

            # إذا لم يكتب --validate
            else:

                # ابنِ تقرير الجرد الذي يحسب الأنواع والأقسام
                report = builder.inventory_report(documents)

            # احفظ التقرير في المسار الذي حدده المستخدم
            # report = بيانات التقرير
            # args.file_path = مسار ملف الإدخال الأصلي
            # args.output = مسار التقرير النهائي
            writer.save(
                report,
                args.file_path,
                args.output
            )

        # إذا لم يكتب --output لكنه كتب --validate
        elif args.validate:

            # اعرض نتيجة التحقق في التيرمنال فقط
            show_validation(documents)

        # إذا لم يكتب --output ولا --validate
        else:

            # اعرض ملخص الجرد القديم في التيرمنال
            show_inventory(documents)

    # التعامل مع الأخطاء المتوقعة أثناء التنفيذ
    except (OSError, ValueError, KeyError, TypeError) as error:

        # اطبع رسالة الخطأ في stderr بدل stdout
        # stderr مخصص لرسائل الأخطاء
        print(f"Error: {error}", file=sys.stderr)

        # أنهِ البرنامج برمز خروج 1
        # الرقم 1 يعني أن العملية فشلت
        sys.exit(1)


# هذا الشرط يتأكد أننا شغّلنا inventory.py مباشرة
# وليس أننا استوردناه من ملف Python آخر
if __name__ == "__main__":

    # ابدأ تشغيل البرنامج من دالة main الوحيدة
    main()
