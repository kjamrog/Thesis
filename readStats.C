#include <iostream>
#include <xAODCore/tools/IOStats.h>
#include <xAODCore/tools/ReadStats.h>

xAOD::ReadStats& getStats() {
  return xAOD::IOStats::instance().stats();
}
