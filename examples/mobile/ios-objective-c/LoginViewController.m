#import <Foundation/Foundation.h>

@interface LoginViewController : NSObject
@end

@implementation LoginViewController

- (void)saveToken:(NSString *)token {
  // Intentional fixture: sensitive token is stored in UserDefaults.
  [[NSUserDefaults standardUserDefaults] setObject:token forKey:@"refresh_token"];
}

@end
