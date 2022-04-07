#include <QApplication>
#include "main_form.h"

int main(int argc, char* argv[]) {
    QApplication a(argc, argv);

    MainForm m;
    m.show();

    return a.exec();
}
